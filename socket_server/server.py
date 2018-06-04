#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals

import json
import time

import redis
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import logging

from cache import init_redis, ROOM_STATUS_KEY, RedisProxy, ROOM_MEMBER_KEY, ROOM_SONG_KEY, KVRedisProxy, \
    USER_SONG_KEY, HashRedisProxy, ListRedisProxy, TIME_ASK, TIME_REST, USER_ROOM_KEY
from celery_tasks import singing_callback, ask_callback, rest_callback
from const import RoomStatus, STATUS_ERROR, STATUS_SUCCESS
from message import WsMessage
from decorators import validate_room

logger = logging.getLogger(__name__)

from tornado.options import define, options
from tornado.gen import coroutine, sleep

from db import session, Room, PartyUser, Song

define("port", default=8888, help="run on the given port", type=int)

redis_room = None


class ChatCenter(object):
    '''
        处理websocket 服务器与客户端交互
    '''
    newer = 'newer'
    chat_register = {'newer': set()}
    members = None
    songs = None
    user = None
    user_song = None
    room = None

    def __init__(self):
        self.members = RedisProxy(redis_room, ROOM_MEMBER_KEY, 'fullname', ['fullname', 'nick', 'avatar'])
        self.songs = ListRedisProxy(redis_room, ROOM_SONG_KEY, 'fullname',
                                    ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link'])
        self.user_song = RedisProxy(redis_room, USER_SONG_KEY, 'fullname', ['fullname'])
        self.user_room = RedisProxy(redis_room, USER_ROOM_KEY, 'fullname', ['fullname'])
        self.room = HashRedisProxy(redis_room, ROOM_STATUS_KEY)

    def parameter_wrapper(self, message):
        parsed = tornado.escape.json_decode(message)
        msg = WsMessage(parsed)
        for k, v in parsed.items():
            setattr(msg, k, v)
        return msg

    @staticmethod
    def get_now_end_time(duration):
        now = int(time.time())
        return now + duration

    def response_wrapper(self, message, status=STATUS_SUCCESS, msg='success'):
        chat = {
            # "id": str(uuid.uuid4()),
            "status": status,
            "body": message,
            "message": msg,
            "timestamp": str(time.time()),
        }
        return chat

    def register(self, newer):
        '''
            保存新加入的客户端连接、监听实例，并向聊天室其他成员发送消息！
        '''
        self.chat_register[self.newer].add(newer)
        logger.info('INFO new socket connecting')

    def unregister(self, lefter):
        '''
            客户端关闭连接，删除聊天室内对应的客户端连接实例
        '''
        room = lefter.room_id
        if not lefter.user:
            self.chat_register[self.newer].remove(lefter)
            logger.info('INFO socket close from room {0}'.format(self.newer))
            return
        self.members.remove_member_from_set(room, lefter.user.fullname, lefter.user.nick, lefter.user.avatar)
        self.user_room.remove_member_from_set(room, lefter.user.fullname)
        # 检查是否排麦
        if self.user_song.exist(room, lefter.user.fullname):
            index = self.songs.search(room, lefter.user.fullname)
            if index > -1:
                self.songs.remove(room, index)
            self.user_song.remove_member_from_set(room, lefter.user.fullname)
        # 检查是否正在演唱
        room_status = self.get_room_info(room)
        status = room_status.get('status')
        if status == RoomStatus.singing and room_status.get('fullname') == lefter.user.fullname:
            room_status = self.room.set_rest(room)
            rest_callback.apply_async((room, self.get_now_end_time(TIME_REST)), countdown=TIME_REST)
        self.boardcast_in_room(None, room_status)
        self.chat_register[room].remove(lefter)
        logger.info('INFO socket {0} close from room {1}'.format(lefter.user.fullname, room))

    @coroutine
    def callback_news(self, sender, message):
        '''
            处理客户端提交的消息
            message : {
                "action": "xx", # 路由
                "body": "xx", # 内容
                "fullname": 'xx',
                "token": "xx"
            }
        '''
        message = self.parameter_wrapper(message)
        logger.info('INFO recv message {0}'.format(message))
        urls = {'join': self.distribute_room,
                'status': self.room_info,
                'ask': self.ask_singing,
                'cut': self.cut_song,
                'sing': self.pick_song,
                'boardcast': self.boardcast_in_room}
        view_func = urls.get(message.action, self.boardcast_in_room)
        if message.action in ['ask', 'cut', 'sing', 'status']:
            if not self.user_room.exist(message.room, message.fullname):
                sender.write_message(self.response_wrapper({}, STATUS_ERROR, '请先进入房间'))
                return
        if message.action in ['join']:
            if self.user_room.exist(message.room, message.fullname):
                sender.write_message(self.response_wrapper({}, STATUS_ERROR, '你已在房间中'))
                return
        yield view_func(sender, message)

        # room = parsed.get("room")
        # send_type = parsed.get("type", 0)
        # token = parsed.get("token", '')
        # if send_type == 1:
        #     self.distribute_room(room, sender)
        #     logger.info('INFO socket enter room {0}'.format(room))
        # elif send_type == 2:
        #     user = session.query(User).filter(User.token == token).first()
        #     if user:
        #         user.active = True
        #         session.commit()
        # sender.write_message(json.dumps({'body': 'pong'}))
        # else:
        #     self.callback_trigger(room, chat)

    def get_room_info(self, room):
        result = self.room.get(room)
        out_dict = {'room': room}
        # room_obj = session.query(Room).filter(Room.room_id == room).first()
        # if room_obj:
        #     out_dict['name'] = room_obj.name
        #     out_dict['cover'] = room_obj.cover
        # 房间人数
        out_dict['count'] = self.members.get_set_count(room)
        out_dict['members'] = self.members.get_set_members(room)
        out_dict['songs'] = self.songs.get_members(room)
        for k, v in result.items():
            out_dict[k] = v
        return out_dict

    # 路由 房间信息
    @coroutine
    def room_info(self, sender, message):
        msg = self.get_room_info(message.room)
        yield sender.write_message(self.response_wrapper(msg))

    # 路由 广播
    @coroutine
    def boardcast_in_room(self, sender, message):
        yield self.callback_trigger(message.get('room'), self.response_wrapper(message))

    @coroutine
    def ask_singing(self, sender, message):
        ack = message.ack
        res = self.get_room_info(message.room)
        if res.get('status') != RoomStatus.ask:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '当前状态不能上麦/不能重复上麦'))
            return
        song = self.songs.get(message.room)
        if song.get('fullname') != message.fullname:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '不能演唱不是自己点的歌~'))
            return
        song = self.songs.pop(message.room)
        song['duration'] = int(song.get('duration'), 0)
        self.user_song.remove_member_from_set(message.room, message.fullname)
        if ack:
            res = self.room.set_song(message.room, song)
            # 广播房间状态
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)
            # 歌曲完成回调
            singing_callback.apply_async((message.room, res.get('end_time')), countdown=int(res.get('duration')))
        else:
            song = self.songs.get(message.room)
            res = self.room.set_ask(message.room, song.get('fullname'), song.get('name'))
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)
            ask_callback.apply_async((message.room, self.get_now_end_time(TIME_ASK)), countdown=TIME_ASK)

    @coroutine
    def cut_song(self, sender, message):
        room_status = self.room.get(message.room)
        if room_status.get('status') != RoomStatus.singing:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '当前不可切歌'))
            return
        if room_status.get('fullname') != message.fullname:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '只有演唱者才能切歌'))
            return
        res = self.room.set_rest(message.room)
        res = self.get_room_info(message.room)
        yield self.boardcast_in_room(sender, res)
        rest_callback.apply_async((message.room, self.get_now_end_time(TIME_REST)), countdown=TIME_REST)


    @coroutine
    def pick_song(self, sender, message):
        sid = message.sid
        song = session.query(Song).filter(Song.id == sid).one()
        if not song:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '歌曲不存在'))
            return
        duration = message.duration
        song.duration = duration
        session.commit()
        if self.user_song.exist(message.room, sender.user.fullname):
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '不能重复排麦'))
            return

        self.songs.push(message.room, song.id, song.name, song.author, sender.user.nick, sender.user.fullname,
                        song.duration, song.lrc, song.link)
        self.user_song.create_update_set(message.room, sender.user.fullname)
        yield sender.write_message(self.response_wrapper({}))

        room_status = self.room.get(message.room)
        if room_status.get('status') == RoomStatus.free:
            song = self.songs.get(message.room)
            res = self.room.set_ask(message.room, song.get('fullname'), song.get('name'))
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)
            ask_callback.apply_async((message.room, self.get_now_end_time(TIME_ASK)), countdown=TIME_ASK)

    @coroutine
    def callback_trigger(self, home, message):
        '''
            消息触发器，将最新消息返回给对应聊天室的所有成员
        '''
        start = time.time()
        for callbacker in self.chat_register[home]:
            try:
                yield callbacker.write_message(json.dumps(message))
            except Exception as e:
                logger.error("ERROR IN sending message: {0}, reason {1}".format(message, e))
        end = time.time()
        logging.info("Send message to {0} waiters, cost {1}s message: {2}".format(len(self.chat_register[home]),
                                                                                  (end - start) * 1000.0, message))

    @coroutine
    def generate_new_room(self, room):
        if room not in self.chat_register:
            room_obj = session.query(Room).filter(Room.room_id == room).first()
            if room_obj:
                self.chat_register[room] = set()
                self.room.set_init(room, room_obj.name, room_obj.cover)
                return True
        return False

    @coroutine
    def distribute_room(self, sender, message):
        result = yield self.generate_new_room(message.room)
        if not result:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '房间不存在'))
            return
        sender.room_id = message.room
        sender.token = message.token
        user = session.query(PartyUser).filter(PartyUser.token == message.token).first()
        if user:
            sender.user = user
            self.chat_register[message.room].add(sender)
            self.chat_register[self.newer].remove(sender)
            self.members.create_update_set(message.room, user.fullname, user.nick, user.avatar)
            self.user_room.create_update_set(message.room, user.fullname)
            # sender.write_message(self.response_wrapper({}))
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)
            return
        yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '用户不存在'))


class Application(tornado.web.Application):
    def __init__(self):
        self.chat_center = ChatCenter()

        handlers = [
            (r"/index", RoomHandler),
            (r"/room", MainHandler),
            (r"/board", BoardCastHandler),
            (r"/", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
        )
        super(Application, self).__init__(handlers, **settings)


class RoomHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render("room.html")


class BoardCastHandler(tornado.web.RequestHandler):
    @coroutine
    def post(self, *args, **kwargs):
        message = json.loads(self.request.body)
        if message.get('room'):
            yield self.application.chat_center.boardcast_in_room(None, message)
            self.write('success')
            return
        self.write('fail')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        room = self.get_argument("room", None)
        if room:
            self.render("index.html", messages=[], room=room)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        self.room_id = None
        self.token = None
        self.user = None
        super(ChatSocketHandler, self).__init__(application, request, **kwargs)

    @coroutine
    def open(self):
        # try:
        yield self.application.chat_center.register(self)  # 记录客户端连接
        # except Exception as e:
        #     logger.error('ERROR IN init web socket , reason {0}'.format(e))
        #     raise e

    @coroutine
    def on_close(self):
        # try:
        yield self.application.chat_center.unregister(self)  # 删除客户端连接
        # except Exception as e:
        #     logger.error('ERROR IN close web socket, reason {0}'.format(e))
        #     raise e

    @coroutine
    def on_message(self, message):
        # try:
        yield self.application.chat_center.callback_news(self, message)  # 处理客户端提交的最新消息
        # except Exception as e:
        #     logger.error('ERROR IN new message coming, message {0}, reason {1}'.format(message, e))
        #     raise e

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}


def main():
    global redis_room
    init_redis()
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

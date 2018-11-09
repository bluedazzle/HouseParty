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
    USER_SONG_KEY, HashRedisProxy, ListRedisProxy, TIME_ASK, TIME_REST, USER_ROOM_KEY, ROOM_MUSIC_KEY, USER_MUSIC_KEY
from celery_tasks import singing_callback, ask_callback, rest_callback, music_callback
from const import RoomStatus, STATUS_ERROR, STATUS_SUCCESS
from message import WsMessage
from decorators import validate_room
from utils import generate_task_id, get_now_timestamp

logger = logging.getLogger(__name__)

from tornado.options import define, options
from tornado.gen import coroutine, sleep

from db import session, Room, PartyUser, Song, Video

define("port", default=8888, help="run on the given port", type=int)

redis_room = None
redis_common = None


class ChatCenter(object):
    '''
        处理websocket 服务器与客户端交互
    '''
    newer = 'newer'
    chat_register = {'newer': set()}
    chat_history = {}
    members = None
    # songs = None
    user = None
    # user_song = None
    room = None

    def __init__(self):
        self.members = RedisProxy(redis_room, ROOM_MEMBER_KEY, 'fullname', ['fullname', 'nick', 'avatar'])
        # self.songs = ListRedisProxy(redis_room, ROOM_SONG_KEY, 'fullname',
        #                             ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
        # self.music = ListRedisProxy(redis_room, ROOM_MUSIC_KEY, 'fullname',
        #                             ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
        # self.user_song = RedisProxy(redis_room, USER_SONG_KEY, 'fullname', ['fullname'])
        # self.user_music = RedisProxy(redis_room, USER_MUSIC_KEY, 'fullname', ['fullname'])
        self.user_room = RedisProxy(redis_room, USER_ROOM_KEY, 'fullname', ['fullname'])
        self.room = HashRedisProxy(redis_room, ROOM_STATUS_KEY)
        self.kv = KVRedisProxy(redis_common, 'USER_STATUS_{0}', 'fullname',
                               ['fullname', 'nick', 'room_id', 'room_name', 'online'])

    def parameter_wrapper(self, message):
        parsed = tornado.escape.json_decode(message)
        msg = WsMessage(parsed)
        for k, v in parsed.items():
            setattr(msg, k, v)
        return msg

    @staticmethod
    def get_now_end_time(duration):
        now = get_now_timestamp()
        return now + duration

    def response_wrapper(self, message, status=STATUS_SUCCESS, msg='success', msg_type=1, raw_message=None):
        chat = {
            # "id": str(uuid.uuid4()),
            "status": status,
            "type": msg_type,
            "body": message,
            "message": msg,
            "timestamp": str(time.time()),
        }
        if raw_message:
            chat['caller_action'] = raw_message.action
            chat['caller_fullname'] = raw_message.fullname
        if msg_type == 1:
            logger.info('INFO response msg {0}'.format(chat))
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
        if lefter.dead:
            return
        room = lefter.room_id
        if not lefter.user:
            self.chat_register[self.newer].remove(lefter)
            logger.info('INFO socket close from room {0}'.format(self.newer))
            return
        self.members.remove_member_from_set(room, lefter.user.fullname, lefter.user.nick, lefter.user.avatar)
        self.user_room.remove_member_from_set(room, lefter.user.fullname)
        self.room.set_mem_update_time(room)

        # 检查是否排麦
        # if self.user_song.exist(room, lefter.user.fullname):
        #     index = self.songs.search(room, lefter.user.fullname)
        #     if index > -1:
        #         self.songs.remove(room, index)
        #     self.user_song.remove_member_from_set(room, lefter.user.fullname)
        # if self.user_music.exist(room, lefter.user.fullname):
        #     index = self.music.search(room, lefter.user.fullname)
        #     if index > -1:
        #         self.music.remove(room, index)
        #     self.user_music.remove_member_from_set(room, lefter.user.fullname)
        # # 检查是否正在演唱
        # room_status = self.get_room_info(room)
        # status = room_status.get('status')
        # if status == RoomStatus.singing and room_status.get('fullname') == lefter.user.fullname:
        #     task = generate_task_id()
        #     self.room.set_rest(room, task=task)
        #     rest_callback.apply_async((room, self.get_now_end_time(TIME_REST), task, TIME_REST), countdown=TIME_REST)
        # if status == RoomStatus.music and room_status.get('fullname') == lefter.user.fullname:
        #     music = self.music.pop(room)
        #     task = generate_task_id()
        #     if music:
        #         self.user_music.remove_member_from_set(room, music.get('fullname'))
        #         duration = float(music.get('duration'))
        #         res = self.room.set_music(room, music, task)
        #         music_callback.apply_async((room, self.get_now_end_time(duration), task, duration),
        #                                    countdown=duration)
        #     else:
        #         res = self.room.set_rest(room, True, task=task)
        # if status == RoomStatus.music and room_status.get('fullname') == lefter.user.fullname:
        room_status = self.get_room_info(room)
        self.boardcast_in_room(None, room_status)
        self.chat_register[room].remove(lefter)
        self.kv.setex(lefter.user.fullname, 300, lefter.user.fullname, lefter.user.nick, '', '', True)
        # 无人房间删除.exception('ERROR in session commit reason {0}'.format(e))
        # if not self.members.get_set_count(room):
        #     obj = session.query(Room).filter(Room.room_id == room, Room.ding == False).first()
        #     if obj:
        #         session.delete(obj)
        #         session.commit()
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
        msg = ''
        if message.action not in ['heart']:
            for k, v in message.raw.items():
                msg = '{0}\r\n{1}: {2}'.format(msg, k, v)
            logger.info('INFO recv message: {0}'.format(msg))
        urls = {'join': self.distribute_room,
                'status': self.room_info,
                # 'ask': self.ask_singing,
                # 'cut': self.cut_song,
                # 'del': self.del_song,
                # 'sing': self.pick_song,
                'watch': self.pick_video,
                'cut_video': self.cut_video,
                'set_duration': self.set_video_duration,
                # 'del_music': self.del_music,
                # 'cut_music': self.cut_music,
                # 'listen': self.listen_music,
                'heart': self.heart_beat,
                'chat': self.send_chat,
                'close': self.close_user,
                'history': self.get_chat_his,
                'device': self.send_device_msg,
                'reconnect': self.reconnect_room,
                'boardcast': self.boardcast_in_room}
        view_func = urls.get(message.action, None)
        if not view_func:
            return
        if message.action in ['ask', 'cut', 'sing', 'status', 'history', 'chat', 'heart', 'device', 'listen',
                              'del_music', 'cut_music']:
            if not self.user_room.exist(message.room, message.fullname):
                sender.write_message(self.response_wrapper({}, STATUS_ERROR, '请先进入房间', raw_message=message))
                return
        if message.action in ['join']:
            if self.user_room.exist(message.room, message.fullname):
                sender.write_message(self.response_wrapper({}, STATUS_ERROR, '你已在房间中', raw_message=message))
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
        for k, v in result.items():
            out_dict[k] = v
        out_dict['count'] = self.members.get_set_count(room)
        out_dict['members'] = self.members.get_set_members(room)
        # out_dict['songs'] = self.songs.get_members(room)
        # out_dict['musics'] = self.music.get_members(room)
        return out_dict

    @coroutine
    def close_user(self, sender, message):
        sender.write_message(self.response_wrapper({}))
        sender.close()

    # 路由 房间信息
    @coroutine
    def room_info(self, sender, message):
        msg = self.get_room_info(message.room)
        yield sender.write_message(self.response_wrapper(msg, raw_message=message))

    @coroutine
    def get_chat_his(self, sender, message):
        lru = self.chat_history[message.room]
        raw_msg = zip(lru.table.keys(), [itm.value for itm in lru.table.values()])
        output = []
        for k, v in raw_msg:
            v.update({'timestamp': k})
            output.append(v)
        output = sorted(output, key=lambda x: x['timestamp'], reverse=True)
        yield sender.write_message(self.response_wrapper(output, msg_type=2, raw_message=message))

    # 路由 广播
    @coroutine
    def boardcast_in_room(self, sender, message):
        if isinstance(message, WsMessage):
            message = message.raw
            yield self.callback_trigger(message.get('room'), self.response_wrapper(message, raw_message=message))
            return
        yield self.callback_trigger(message.get('room'), self.response_wrapper(message))

    # 心跳包
    @coroutine
    def heart_beat(self, sender, message):
        yield sender.write_message(self.response_wrapper({'heart': 'success'}, msg_type=2, raw_message=message))

    # 聊天
    @coroutine
    def send_chat(self, sender, message):
        lru = self.chat_history.get(message.room)
        chat = {'fullname': sender.user.fullname, 'nick': sender.user.nick, 'content': message.content}
        lru[time.time()] = chat
        chat['action'] = 'chat'
        chat['room'] = message.room
        yield self.callback_trigger(message.room, self.response_wrapper(chat, msg_type=2, raw_message=message))

    # 设备消息
    @coroutine
    def send_device_msg(self, sender, message):
        msg = {'fullname': message.fullname, "room": message.room}
        msg["device"] = message.device
        msg["value"] = message.value
        yield self.callback_trigger(message.room, self.response_wrapper(msg, msg_type=2, raw_message=message))

    @coroutine
    def ask_singing(self, sender, message):
        ack = message.ack
        res = self.get_room_info(message.room)
        if res.get('status') != RoomStatus.ask:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '当前状态不能上麦/不能重复上麦', raw_message=message))
            return
        song = self.songs.get(message.room)
        if song.get('fullname') != message.fullname:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '不能演唱不是自己点的歌~', raw_message=message))
            return
        song = self.songs.pop(message.room)
        song['duration'] = float(song.get('duration'))
        self.user_song.remove_member_from_set(message.room, message.fullname)
        if ack:
            # celery task id
            task = generate_task_id()
            res = self.room.set_song(message.room, song, task)
            # 广播房间状态
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)
            # 歌曲完成回调
            singing_callback.apply_async((message.room, res.get('end_time'), task, res.get('duration')),
                                         countdown=float(res.get('duration')))
        else:
            song = self.songs.get(message.room)
            if not song:
                self.room.set_rest(message.room, True)
            else:
                task = generate_task_id()
                self.room.set_ask(message.room, song.get('fullname'), song.get('name'), task)
                ask_callback.apply_async((message.room, self.get_now_end_time(TIME_ASK), task, TIME_ASK),
                                         countdown=TIME_ASK)
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)

    @coroutine
    def cut_video(self, sender, message):
        room_status = self.room.get(message.room)
        if room_status.get('status') != RoomStatus.singing:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '当前没有视频可切', raw_message=message))
            return
        if room_status.get('fullname') != message.fullname:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '只有点播者才能切视频', raw_message=message))
            return
        task = generate_task_id()
        res = self.room.set_rest(message.room, True, task=task)
        res = self.get_room_info(message.room)
        yield self.boardcast_in_room(sender, res)

    @coroutine
    def cut_song(self, sender, message):
        room_status = self.room.get(message.room)
        if room_status.get('status') != RoomStatus.singing:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '当前不可切歌', raw_message=message))
            return
        if room_status.get('fullname') != message.fullname:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '只有演唱者才能切歌', raw_message=message))
            return
        task = generate_task_id()
        res = self.room.set_rest(message.room, task=task)
        res = self.get_room_info(message.room)
        yield self.boardcast_in_room(sender, res)
        rest_callback.apply_async((message.room, self.get_now_end_time(TIME_REST), task, TIME_REST),
                                  countdown=TIME_REST)

    @coroutine
    def cut_music(self, sender, message):
        room_status = self.room.get(message.room)
        if room_status.get('status') != RoomStatus.music:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '当前不可切音乐', raw_message=message))
            return
        if room_status.get('fullname') != message.fullname:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '只有点歌者才能切音乐', raw_message=message))
            return
        task = generate_task_id()
        music = self.music.pop(message.room)
        if music:
            self.user_music.remove_member_from_set(message.room, message.fullname)
            duration = float(music.get('duration'))
            res = self.room.set_music(message.room, music, task)
            music_callback.apply_async((message.room, self.get_now_end_time(duration), task, duration),
                                       countdown=duration)
        else:
            res = self.room.set_rest(message.room, True, task=task)
        res = self.get_room_info(message.room)
        yield self.boardcast_in_room(sender, res)

    @coroutine
    def del_music(self, sender, message):
        index = self.music.search(message.room, message.fullname)
        if index > -1:
            self.music.remove(message.room, index)
            self.user_music.remove_member_from_set(message.room, message.fullname)
            yield sender.write_message(self.response_wrapper({}, msg='取消点歌成功', raw_message=message))
            room_status = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, room_status)
            return
        else:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, msg='未找到已点歌曲', raw_message=message))

    @coroutine
    def del_song(self, sender, message):
        index = self.songs.search(message.room, message.fullname)
        if index > -1:
            self.songs.remove(message.room, index)
            self.user_song.remove_member_from_set(message.room, message.fullname)
            yield sender.write_message(self.response_wrapper({}, msg='取消点歌成功', raw_message=message))
            room_status = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, room_status)
            return
        else:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, msg='未找到已点歌曲', raw_message=message))

    @coroutine
    def set_video_duration(self, sender, message):
        room_status = self.get_room_info(message.room)
        current = message.current
        if room_status.get('status') != RoomStatus.singing:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '当前无播放视频', raw_message=message))
            return
        if current > int(room_status.get('duration')) or current < 0:
            yield sender.write_message(self.response_wrapper({}, msg='进度调整错误', raw_message=message))
            return
        if current == int(room_status.get('duration')):
            self.room.set_rest(message.room, True)
        else:
            self.room.set_progress(message.room, current, int(room_status.get('duration')))
        room_status = self.get_room_info(message.room)
        yield self.boardcast_in_room(sender, room_status)

    @coroutine
    def pick_video(self, sender, message):
        room_status = self.get_room_info(message.room)
        if room_status.get('status') != RoomStatus.free:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '视频已经在播放中啦', raw_message=message))
            return
        vid = message.vid
        video = session.query(Video).filter(Video.id == vid).one()
        if not video:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '视频不存在', raw_message=message))
            return
        obj = {'name': video.name, 'duration': video.duration, 'url': video.url}
        res = self.room.set_video(message.room, sender.user.fullname, obj, 'none')
        room_status = self.get_room_info(message.room)
        yield self.boardcast_in_room(sender, room_status)

    @coroutine
    def pick_song(self, sender, message):
        room_status = self.get_room_info(message.room)
        count = self.music.get_count(message.room)
        if count or room_status.get('status') == RoomStatus.music:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '听歌时不能唱歌哟', raw_message=message))
            return
        sid = message.sid
        song = session.query(Song).filter(Song.id == sid).one()
        if not song:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '歌曲不存在', raw_message=message))
            return
        duration = message.duration
        song.duration = duration
        session.commit()
        if self.user_song.exist(message.room, sender.user.fullname):
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '不能重复排麦', raw_message=message))
            return

        self.songs.push(message.room, song.id, song.name, song.author, sender.user.nick, sender.user.fullname,
                        song.duration, song.lrc, song.link, sender.user.avatar)
        self.user_song.create_update_set(message.room, sender.user.fullname)
        yield sender.write_message(self.response_wrapper({}, raw_message=message))
        room_status = self.get_room_info(message.room)

        if room_status.get('status') == RoomStatus.free:
            song = self.songs.get(message.room)
            task = generate_task_id()
            res = self.room.set_ask(message.room, song.get('fullname'), song.get('name'), task)
            room_status = self.get_room_info(message.room)
            ask_callback.apply_async((message.room, self.get_now_end_time(TIME_ASK), task, TIME_ASK),
                                     countdown=TIME_ASK)
        yield self.boardcast_in_room(sender, room_status)

    # 听歌
    @coroutine
    def listen_music(self, sender, message):
        room_status = self.get_room_info(message.room)
        count = self.songs.get_count(message.room)
        if count or room_status.get('status') == RoomStatus.singing:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '唱歌时不能听歌哟', raw_message=message))
            return
        sid = message.sid
        song = session.query(Song).filter(Song.id == sid).one()
        if not song:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '歌曲不存在', raw_message=message))
            return
        duration = message.duration
        song.duration = duration
        session.commit()
        if self.user_music.exist(message.room, sender.user.fullname):
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '不能重复排歌', raw_message=message))
            return

        self.music.push(message.room, song.id, song.name, song.author, sender.user.nick, sender.user.fullname,
                        song.duration, song.lrc, song.original, sender.user.avatar)
        self.user_music.create_update_set(message.room, sender.user.fullname)
        yield sender.write_message(self.response_wrapper({}, raw_message=message))
        room_status = self.get_room_info(message.room)

        if room_status.get('status') == RoomStatus.free:
            song = self.music.pop(message.room)
            self.user_music.remove_member_from_set(message.room, message.fullname)
            task = generate_task_id()
            duration = float(song.get('duration'))
            res = self.room.set_music(message.room, song, task)
            room_status = self.get_room_info(message.room)
            music_callback.apply_async((message.room, self.get_now_end_time(duration), task, duration),
                                       countdown=duration)
        yield self.boardcast_in_room(sender, room_status)

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
        import pylru
        room_obj = session.query(Room).filter(Room.room_id == room).first()
        if not room_obj:
            return False, None
        if room not in self.chat_register:
            self.chat_register[room] = set()
            self.chat_history[room] = pylru.lrucache(200)
            self.room.set_init(room, room_obj.name, room_obj.cover)
        return True, room_obj

    @coroutine
    def distribute_room(self, sender, message):
        result, obj = yield self.generate_new_room(message.room)
        if not result:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '房间不存在', raw_message=message))
            return
        if len(self.chat_register[message.room]) >= 12:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '房间人数已满', raw_message=message))
            sender.close()
            return
        sender.room_id = message.room
        sender.token = message.token
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception('ERROR in session commit reason {0}'.format(e))
        user = session.query(PartyUser).filter(PartyUser.token == message.token).first()
        if user:
            sender.user = user
            self.chat_register[message.room].add(sender)
            self.chat_register[self.newer].remove(sender)
            self.members.create_update_set(message.room, user.fullname, user.nick, user.avatar)
            self.user_room.create_update_set(message.room, user.fullname)
            # sender.write_message(self.response_wrapper({}))
            self.room.set_mem_update_time(message.room)
            self.kv.set(user.fullname, user.fullname, user.nick, message.room, obj.name, True)
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)
            return
        yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '用户不存在', raw_message=message))

    @coroutine
    def reconnect_room(self, sender, message):
        result = yield self.generate_new_room(message.room)
        if not result:
            yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '房间不存在', raw_message=message))
            return
        sender.room_id = message.room
        sender.token = message.token
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception('ERROR in session commit reason {0}'.format(e))

        user = session.query(PartyUser).filter(PartyUser.token == message.token).first()
        if user:
            sender.user = user
            self.remove_dead_user(message.room, user)
            self.chat_register[message.room].add(sender)
            self.chat_register[self.newer].remove(sender)
            self.members.create_update_set(message.room, user.fullname, user.nick, user.avatar)
            self.user_room.create_update_set(message.room, user.fullname)
            # sender.write_message(self.response_wrapper({}))
            res = self.get_room_info(message.room)
            yield self.boardcast_in_room(sender, res)
            return
        yield sender.write_message(self.response_wrapper({}, STATUS_ERROR, '用户不存在', raw_message=message))

    def remove_dead_user(self, room, user):
        socket_set = self.chat_register[room]
        dead = None
        for socket in socket_set:
            if socket.user.fullname == user.fullname:
                dead = socket
                break
        if dead:
            dead.dead = 1
            dead.close()
            self.chat_register[room].remove(dead)


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
            websocket_ping_interval=5,
            websocket_ping_timeout=30,
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
            logger.info('INFO http boardcast msg: {0}'.format(message))
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
        self.dead = 0
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

    def on_pong(self, data):
        logger.info('INFO on pong {0}'.format(self.user))

    def on_ping(self, data):
        logger.info('INFO on ping {0}'.format(self.user))

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}


def main():
    global redis_room, redis_common
    init_redis()
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    redis_common = redis.StrictRedis(host='localhost', port=6379, db=4)
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

# coding: utf-8

from __future__ import unicode_literals
import jpush as jpush
import redis

from socket_server.cache import KVRedisProxy

APP_KEY = '8a3d8a574a0137f8e153ddf1'
MASTER_SECRET = 'b593a0b85c902c0d2261b4d0'


def push_to_friends(tag, fullname):
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("ERROR")
    msg = "好友{0}上线啦~".format(fullname).encode('utf-8')
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg)
    push.audience = jpush.audience(
        jpush.alias(tag)
    )
    # push.notification = jpush.notification(alert="上线啦~", ios=ios_msg)
    push.platform = jpush.all_
    push.options = {"apns_production": True}
    # print (push.payload)
    # push.message = jpush.message(msg_content=msg, title=msg)
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    try:
        push.send()
    except:
        pass


def push_friend_response(rid, user):
    msg = '{0} 同意了你的好友请求'.format(user.fullname).encode('utf-8')
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("ERROR")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg)
    push.audience = jpush.audience(
        jpush.alias(rid)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    push.platform = jpush.all_
    push.options = {"apns_production": True}
    # print (push.payload)
    try:
        push.send()
    except:
        pass


def push_friend_request(rid, user):
    msg = '{0} 想添加您为好友'.format(user.fullname).encode('utf-8')
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("ERROR")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg)
    push.audience = jpush.audience(
        jpush.alias(rid)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    push.platform = jpush.all_
    push.options = {"apns_production": True}
    # print (push.payload)
    try:
        push.send()
    except:
        pass


def push_hook(user, to):
    r = redis.StrictRedis(host='localhost', port=6379, db=4)
    kv = KVRedisProxy(r, 'USER_STATUS_{0}', 'fullname',
                      ['fullname', 'nick', 'room_id', 'room_name', 'online'])
    user_data = kv.get(user)
    msg = '{0} 向你打招呼, 点击加入聊天'.format(user_data.get('nick'))
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("DEBUG")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg,
                        extras={'room_id': user_data.get('room_id'), 'room_name': user_data.get('room_name')})
    android_msg = jpush.android(alert=msg,
                                extras={'room_id': user_data.get('room_id'), 'room_name': user_data.get('room_name')})
    push.audience = jpush.audience(
        jpush.alias(to)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg, android=android_msg)
    push.platform = jpush.all_
    push.options = {"apns_production": True}
    try:
        push.send()
    except Exception as e:
        print e
        pass


if __name__ == '__main__':
    push_hook('427304', '425029')

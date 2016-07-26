# coding: utf-8

from __future__ import unicode_literals
import jpush as jpush

APP_KEY = '8a3d8a574a0137f8e153ddf1'
MASTER_SECRET = 'b593a0b85c902c0d2261b4d0'


def push_to_friends(tag):
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("ERROR")
    msg = "上线啦~".encode('utf-8')
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg)
    push.audience = jpush.audience(
        jpush.tag(tag, )
    )
    # push.notification = jpush.notification(alert="上线啦~", ios=ios_msg)
    push.platform = jpush.all_
    # print (push.payload)
    push.message = jpush.message(msg_content=msg, title=msg)
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
    # print (push.payload)
    try:
        push.send()
    except:
        pass


def push_hook(rid, user):
    msg = '{0} 向你打招呼, 点击加入聊天'.format(user.fullname).encode('utf-8')
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("DEBUG")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg, extras={'room_id': user.room.room_id})
    push.audience = jpush.audience(
        jpush.alias(rid)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    push.platform = jpush.all_
    # print (push.payload)
    try:
        push.send()
    except:
        pass


class too(object):
    pass


user = too()
setattr(user, 'fullname', 'test')

push_friend_request('18310160189', user)
# coding: utf-8

from __future__ import unicode_literals
import jpush as jpush

APP_KEY = '8a3d8a574a0137f8e153ddf1'
MASTER_SECRET = 'b593a0b85c902c0d2261b4d0'


def push_to_friends(tag):
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("DEBUG")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert="上线啦~", badge="+1", extras={'k1': 'v1'})
    push.audience = jpush.audience(
        jpush.tag(tag, )
    )
    # push.notification = jpush.notification(alert="上线啦~", ios=ios_msg)
    push.platform = jpush.all_
    # print (push.payload)
    push.message = jpush.message(msg_content="上线啦~", title="上线啦~", extras={'k1': 'v1'})
    push.send()


def push_friend_response(rid, user):
    msg = '{0} 同意了你的好友请求'.format(user.fullname)
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("DEBUG")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg, badge="+1", extras={'k1': 'v1'})
    push.audience = jpush.audience(
        jpush.registration_id(rid)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    push.platform = jpush.all_
    # print (push.payload)
    push.send()


def push_friend_request(rid, user):
    msg = '{0} 想添加您为好友'.format(user.fullname)
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("DEBUG")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg, badge="+1", extras={'k1': 'v1'})
    push.audience = jpush.audience(
        jpush.registration_id(rid)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    push.platform = jpush.all_
    # print (push.payload)
    push.send()


def push_hook(rid, user):
    msg = '{0} 向你打招呼, 点击加入聊天'.format(user.fullname)
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    _jpush.set_logging("DEBUG")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg, badge="+1", extras={'room_id': user.room.room_id})
    push.audience = jpush.audience(
        jpush.registration_id(rid)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    push.platform = jpush.all_
    # print (push.payload)
    push.send()

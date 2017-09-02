# coding: utf-8

from __future__ import unicode_literals
import jpush as jpush

APP_KEY = '0912e5412917baa18a835b79'
MASTER_SECRET = '672baf2f36427300b791507a'


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


def push_hook(rid, user):
    msg = '{0} 向你打招呼, 点击加入聊天'.format(user.fullname).encode('utf-8')
    _jpush = jpush.JPush(APP_KEY, MASTER_SECRET)
    # _jpush.set_logging("DEBUG")
    push = _jpush.create_push()
    ios_msg = jpush.ios(alert=msg, extras={'room_id': user.room.room_id})
    push.audience = jpush.audience(
        jpush.alias(rid)
    )
    push.notification = jpush.notification(alert=msg, ios=ios_msg)
    push.platform = jpush.all_
    push.options = {"apns_production": True}
    try:
        push.send()
    except Exception as e:
        print e
        pass


class too(object):
    pass


# user = too()
# room = too()
# setattr(room, 'room_id', '123')
# setattr(user, 'fullname', 'testserver')
# setattr(user, 'room', room)
#
# push_hook('18310160177', user)
#
# class too(object):
#     pass
#
#
# user = too()
# room = too()
# setattr(user, 'fullname', 'test')
# setattr(room, 'room_id', '123')
# setattr(user, 'room', room)
#
# push_hook('18310160178', user)

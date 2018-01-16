# coding: utf-8
from __future__ import unicode_literals

import socketio
import gevent

sio = socketio.Server()
NAMESPACE = '/ktv'
ROOM_EVENT_RESPONSE = 'room response'


@sio.on('join', namespace=NAMESPACE)
def join(sid, message):
    sio.enter_room(sid, message['room'], namespace=NAMESPACE)
    room = message.get('room')
    members = sio.manager.rooms[NAMESPACE][room]
    # 获取 members 详情
    sio.emit(ROOM_EVENT_RESPONSE, {'data': 'Entered room: ' + message['room'], 'members': members},
             room=sid, namespace=NAMESPACE)


@sio.on('leave', namespace=NAMESPACE)
def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace=NAMESPACE)
    room = message.get('room')
    members = sio.manager.rooms[NAMESPACE][room]
    # 获取 members 详情
    sio.emit(ROOM_EVENT_RESPONSE, {'data': 'Left room: ' + message['room'], 'members': members},
             room=sid, namespace=NAMESPACE)


def search_sid(sid):
    rooms = sio.manager.rooms[NAMESPACE]
    for k, v in rooms.items():
        for ssid, is_in in v.items():
            if ssid == sid and is_in:
                return k
    return None


@sio.on('disconnect', namespace=NAMESPACE)
def disconnect(sid):
    room = search_sid(sid)
    if room:
        members = sio.manager.rooms[NAMESPACE][room]
        # 获取 members 详情
        sio.emit(ROOM_EVENT_RESPONSE, {'data': 'Left room: ' + message['room'], 'members': members},
                 room=sid, namespace=NAMESPACE)

# coding: utf-8
from __future__ import unicode_literals

import json
import os
import redis
import logging
import requests
import time

from celery import Celery

from cache import init_redis, RedisProxy, KVRedisProxy, HashRedisProxy, ROOM_STATUS_KEY, USER_SONG_KEY, ROOM_SONG_KEY, \
    ROOM_MEMBER_KEY, redis_room, ListRedisProxy, TIME_REST
from const import RoomStatus
from utils import send_board_cast_msg
from cache import members, songs, user_song, room

app = Celery('celery_task', backend='redis://localhost:6379/2', broker='redis://localhost:6379/2')

app.config_from_object('celery_config')

@app.task()
def singing_callback(key, end_time):
    init_redis()
    now = int(time.time())
    room_status = room.get(key)
    status = room_status.get('status')
    if status != RoomStatus.singing:
        logging.warning(
            'WARNING in singing callback room {0} is not in singing status, now status {1}'.format(key, status))
        return
    if now < end_time:
        logging.warning(
            'WARNING in singing callback room {0} song is not over yet, end time {1} now {2}'.format(key, end_time,
                                                                                                     now))
        delay = end_time - now + 2
        singing_callback.apply_async((key, end_time), countdown=delay)
        return
    res = room.set_rest(key)
    # 广播其他人状态
    send_board_cast_msg(res)
    rest_callback.apply_async((key, end_time), countdown=TIME_REST)
    logging.info('SUCCESS set room {0} to rest info {1}'.format(key, res))


@app.task()
def rest_callback(key, end_time):
    init_redis()
    now = int(time.time())
    room_status = room.get(key)
    status = room_status.get('status')
    if status != RoomStatus.rest:
        logging.warning(
            'WARNING in rest callback room {0} is not in rest status, now status {1}'.format(key, status))
        return
    if now < end_time:
        logging.warning(
            'WARNING in rest callback room {0} rest is not over yet, end time {1} now {2}'.format(key, end_time,
                                                                                                  now))
        delay = end_time - now + 2
        rest_callback.apply_async((key, end_time), countdown=delay)
        return
    song = songs.get(key)
    if not song:
        res = room.set_rest(key, True)
    else:
        res = room.set_ask(key, song.get('fullname'), song.get('name'))
        logging.info('SUCCESS set room {0} to ask info {1}'.format(key, res))
    # 广播
    send_board_cast_msg(res)


@app.task()
def ask_callback(key, end_time):
    import redis
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    members = RedisProxy(redis_room, ROOM_MEMBER_KEY, 'fullname', ['fullname', 'nick', 'avatar'])
    songs = ListRedisProxy(redis_room, ROOM_SONG_KEY, 'fullname', ['sid', 'name', 'author', 'nick', 'fullname'])
    user_song = RedisProxy(redis_room, USER_SONG_KEY, 'fullname', ['fullname'])
    room = HashRedisProxy(redis_room, ROOM_STATUS_KEY)

    now = int(time.time())
    room_status = room.get(key)
    status = room_status.get('status')
    if status != RoomStatus.ask:
        logging.warning(
            'WARNING in rest callback room {0} is not in ask status, now status {1}'.format(key, status))
        return
    if now < end_time:
        logging.warning(
            'WARNING in rest callback room {0} ask is not over yet, end time {1} now {2}'.format(key, end_time,
                                                                                                 now))
        delay = end_time - now + 1
        ask_callback.apply_async((key, end_time), countdown=delay)
        return
    song = songs.pop(key)
    user_song.remove_member_from_set(key, song.get('fullname'))
    song = songs.get(key)
    if not song:
        res = room.set_rest(key, True)
    else:
        res = room.set_ask(key, song.get('fullname'), song.get('name'))
    # 广播
    send_board_cast_msg(res)

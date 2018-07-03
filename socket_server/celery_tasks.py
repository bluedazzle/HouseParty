# coding: utf-8
from __future__ import unicode_literals

import redis
import logging
import time
import datetime

from celery import Celery, current_app

from cache import RedisProxy, HashRedisProxy, ROOM_STATUS_KEY, USER_SONG_KEY, ROOM_SONG_KEY, \
    ROOM_MEMBER_KEY, ListRedisProxy, TIME_REST, TIME_ASK, ROOM_MUSIC_KEY, USER_MUSIC_KEY
from const import RoomStatus
from utils import send_board_cast_msg, generate_task_id

app = Celery('celery_task', backend='redis://localhost:6379/2', broker='redis://localhost:6379/2')

app.config_from_object('celery_config')


# 歌曲唱完后的回调
@app.task()
def singing_callback(key, end_time, task_id, duration):
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    room = HashRedisProxy(redis_room, ROOM_STATUS_KEY)
    songs = ListRedisProxy(redis_room, ROOM_SONG_KEY, 'fullname',
                           ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    musics = ListRedisProxy(redis_room, ROOM_MUSIC_KEY, 'fullname',
                            ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    user_music = RedisProxy(redis_room, USER_MUSIC_KEY, 'fullname', ['fullname'])

    now = float(time.time())
    end_time = float(end_time)
    end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    logging.info('INFO sing exec time {0:%Y-%m-%d %H:%M:%S} end time {1}, duration {2}'.format(datetime.datetime.now(),
                                                                                               end_time_str, duration))
    room_status = room.get(key)
    status = room_status.get('status')
    task = room_status.get('task')
    if task and task != task_id:
        logging.warning(
            'WARNING in singing callback room {0} task invalid, now task {1} celery task {2}'.format(key, task,
                                                                                                     task_id))
        return key
    if status != RoomStatus.singing:
        logging.warning(
            'WARNING in singing callback room {0} is not in singing status, now status {1}'.format(key, status))
        return key
    if now < end_time:
        logging.warning(
            'WARNING in singing callback room {0} song is not over yet, end time {1} now {2}'.format(key, end_time,
                                                                                                     now))
        delay = end_time - now + 2
        current_app.send_task('celery_tasks.singing_callback', args=[key, end_time, task_id, duration], countdown=delay)
        # singing_callback.apply_async((key, end_time), countdown=delay)
        return key
    task = generate_task_id()
    res = room.set_rest(key, task=task)
    res['songs'] = songs.get_members(key)
    res['musics'] = musics.get_members(key)
    # 广播其他人状态
    send_board_cast_msg(res)
    current_app.send_task('celery_tasks.rest_callback', args=[key, end_time, task, duration], countdown=TIME_REST)
    # rest_callback.apply_async((key, end_time), countdown=TIME_REST)
    logging.info('SUCCESS set room {0} to rest info {1}'.format(key, res))
    return key


# 音乐回调
@app.task()
def music_callback(key, end_time, task_id, duration):
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    room = HashRedisProxy(redis_room, ROOM_STATUS_KEY)
    songs = ListRedisProxy(redis_room, ROOM_SONG_KEY, 'fullname',
                           ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    musics = ListRedisProxy(redis_room, ROOM_MUSIC_KEY, 'fullname',
                            ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    user_music = RedisProxy(redis_room, USER_MUSIC_KEY, 'fullname', ['fullname'])
    user_song = RedisProxy(redis_room, USER_SONG_KEY, 'fullname', ['fullname'])

    now = float(time.time())
    end_time = float(end_time)
    end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    logging.info('INFO music exec time {0:%Y-%m-%d %H:%M:%S} end time {1}, duration {2}'.format(datetime.datetime.now(),
                                                                                                end_time_str, duration))
    room_status = room.get(key)
    status = room_status.get('status')
    task = room_status.get('task')
    if task and task != task_id:
        logging.warning(
            'WARNING in music callback room {0} task invalid, now task {1} celery task {2}'.format(key, task,
                                                                                                   task_id))
        return key
    if status != RoomStatus.music:
        logging.warning(
            'WARNING in music callback room {0} is not in music status, now status {1}'.format(key, status))
        return key
    if now < end_time:
        logging.warning(
            'WARNING in music callback room {0} song is not over yet, end time {1} now {2}'.format(key, end_time,
                                                                                                   now))
        delay = end_time - now + 2
        current_app.send_task('celery_tasks.music_callback', args=[key, end_time, task_id, duration], countdown=delay)
        # singing_callback.apply_async((key, end_time), countdown=delay)
        return key
    music = musics.pop(key)
    user_music.remove_member_from_set(key, music.get('fullname'))
    # music = musics.get(key)
    if not music:
        song = songs.get(key)
        # user_song.remove_member_from_set(key, song.get('fullname'))
        if not song:
            res = room.set_rest(key, True)
        else:
            task = generate_task_id()
            res = room.set_ask(key, song.get('fullname'), song.get('name'), task)
            res['songs'] = songs.get_members(key)
            end_time = float(time.time()) + TIME_ASK
            current_app.send_task('celery_tasks.ask_callback', args=[key, end_time, task, duration], countdown=TIME_ASK)
    else:
        duration = float(music.get('duration'))
        task = generate_task_id()
        res = room.set_music(key, music, task)
        end_time = float(time.time()) + duration
        current_app.send_task('celery_tasks.music_callback', args=[key, end_time, task, duration],
                              countdown=duration)
    res['songs'] = songs.get_members(key)
    res['musics'] = musics.get_members(key)
    # 广播其他人状态
    send_board_cast_msg(res)
    logging.info('SUCCESS set room {0} to music info {1}'.format(key, res))
    return key


# 休息完成后的回调
@app.task()
def rest_callback(key, end_time, task_id, duration):
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    songs = ListRedisProxy(redis_room, ROOM_SONG_KEY, 'fullname',
                           ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    musics = ListRedisProxy(redis_room, ROOM_MUSIC_KEY, 'fullname',
                            ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    room = HashRedisProxy(redis_room, ROOM_STATUS_KEY)

    now = float(time.time())
    room_status = room.get(key)
    status = room_status.get('status')
    task = room_status.get('task')
    end_time = float(end_time)
    end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    logging.info('INFO rest exec time {0:%Y-%m-%d %H:%M:%S} end time {1}, duration {2}'.format(datetime.datetime.now(),
                                                                                               end_time_str, duration))
    if task and task != task_id:
        logging.warning(
            'WARNING in rest callback room {0} task invalid, now task {1} celery task {2}'.format(key, task, task_id))
        return
    if status != RoomStatus.rest:
        logging.warning(
            'WARNING in rest callback room {0} is not in rest status, now status {1}'.format(key, status))
        return key
    if now < end_time:
        logging.warning(
            'WARNING in rest callback room {0} rest is not over yet, end time {1} now {2}'.format(key, end_time,
                                                                                                  now))
        delay = end_time - now + 2
        # rest_callback.apply_async((key, end_time), countdown=delay)
        current_app.send_task('celery_tasks.rest_callback', args=[key, end_time, task_id, duration], countdown=delay)
        return key
    song = songs.get(key)
    music = musics.pop(key)
    if not song and not music:
        res = room.set_rest(key, True)
    else:
        task = generate_task_id()
        if song:
            res = room.set_ask(key, song.get('fullname'), song.get('name'), task)
            end_time = float(time.time()) + TIME_ASK
            current_app.send_task('celery_tasks.ask_callback', args=[key, end_time, task, TIME_ASK], countdown=TIME_ASK)
        else:
            res = room.set_music(key, music, task)
            duration = float(music.get('duration'))
            end_time = float(time.time()) + duration
            current_app.send_task('celery_tasks.music_callback', args=[key, end_time, task, duration],
                                  countdown=duration)
    res['songs'] = songs.get_members(key)
    res['musics'] = musics.get_members(key)
    logging.info('SUCCESS set room {0} to ask info {1}'.format(key, res))
    # 广播
    send_board_cast_msg(res)
    return key


# 上麦询问回调
@app.task()
def ask_callback(key, end_time, task_id, duration):
    redis_room = redis.StrictRedis(host='localhost', port=6379, db=5)
    members = RedisProxy(redis_room, ROOM_MEMBER_KEY, 'fullname', ['fullname', 'nick', 'avatar'])
    songs = ListRedisProxy(redis_room, ROOM_SONG_KEY, 'fullname',
                           ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    musics = ListRedisProxy(redis_room, ROOM_MUSIC_KEY, 'fullname',
                            ['sid', 'name', 'author', 'nick', 'fullname', 'duration', 'lrc', 'link', 'avatar'])
    user_song = RedisProxy(redis_room, USER_SONG_KEY, 'fullname', ['fullname'])
    room = HashRedisProxy(redis_room, ROOM_STATUS_KEY)

    now = float(time.time())
    end_time = float(end_time)
    end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    logging.info('INFO ask exec time {0:%Y-%m-%d %H:%M:%S} end time {1}, duration {2}'.format(datetime.datetime.now(),
                                                                                              end_time_str, duration))
    room_status = room.get(key)
    status = room_status.get('status')
    task = room_status.get('task')
    if task and task != task_id:
        logging.warning(
            'WARNING in ask callback room {0} task invalid, now task {1} celery task {2}'.format(key, task, task_id))
        return key
    if status != RoomStatus.ask:
        logging.warning(
            'WARNING in ask callback room {0} is not in ask status, now status {1}'.format(key, status))
        return key
    if now < end_time:
        logging.warning(
            'WARNING in ask callback room {0} ask is not over yet, end time {1} now {2}'.format(key, end_time,
                                                                                                now))
        delay = end_time - now + 1
        current_app.send_task('celery_tasks.ask_callback', args=[key, end_time, task_id, duration], countdown=delay)
        # ask_callback.apply_async((key, end_time), countdown=delay)
        return key
    song = songs.pop(key)
    user_song.remove_member_from_set(key, song.get('fullname'))
    song = songs.get(key)
    if not song:
        res = room.set_rest(key, True)
    else:
        task = generate_task_id()
        res = room.set_ask(key, song.get('fullname'), song.get('name'), task)
        res['songs'] = songs.get_members(key)
        end_time = float(time.time()) + TIME_ASK
        current_app.send_task('celery_tasks.ask_callback', args=[key, end_time, task, duration], countdown=TIME_ASK)
        # ask_callback.apply_async((key, end_time), countdown=TIME_ASK)
    # 广播
    send_board_cast_msg(res)
    return key

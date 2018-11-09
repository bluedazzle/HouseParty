# coding: utf-8
from __future__ import unicode_literals

import redis
from django.core.management.base import BaseCommand

from core.models import Room
from socket_server.cache import RedisProxy, ROOM_MEMBER_KEY


class Command(BaseCommand):
    def handle(self, *args, **options):
        redis_room = redis.StrictRedis(host='localhost', port=6379, db=7)
        members = RedisProxy(redis_room, ROOM_MEMBER_KEY, 'fullname', ['fullname', 'nick', 'avatar'])
        rooms = Room.objects.filter(ding=False).all()
        total = rooms.count()
        for i, room in enumerate(rooms):
            count = members.get_set_count(room.room_id)
            if not count:
                room.delete()
                print 'del {0} {1}/{2}'.format(room.room_id, i+1, total)

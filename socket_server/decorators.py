# coding: utf-8
from __future__ import unicode_literals

import time

from cache import user_room
from const import STATUS_ERROR


def validate_room(func):
    def wraper(*args, **kwargs):
        sender = args[0]
        message = args[1]
        fullname = message.fullname
        room = message.room
        if user_room.exist(room, fullname):
            return func(*args, **kwargs)
        chat = {
            # "id": str(uuid.uuid4()),
            "status": STATUS_ERROR,
            "body": {},
            "message": '请先进入房间',
            "timestamp": str(time.time()),
        }
        sender.write_message(chat)
        return

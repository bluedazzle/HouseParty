# coding: utf-8

from __future__ import unicode_literals

import datetime

import pytz

from scripts.models import session, User, Singer


def check_user():
    users = session.query(User).filter(User.online == True).all()
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    for user in users:
        active = user.modify_time
        if now - active > datetime.timedelta(seconds=40):
            user.online = False
            del_song(user.id, user.room_id)
    session.commit()


def del_song(user_id, room_id):
    if not room_id:
        return
    singers = session.query(Singer).filter(Singer.creator_id == user_id, Singer.room_id == room_id).delete()


if __name__ == '__main__':
    check_user()

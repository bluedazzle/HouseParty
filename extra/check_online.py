#!/usr/bin/python
# coding: utf-8

from __future__ import unicode_literals

import pytz
import datetime

from models import PartyUser, Room, DBSession, Singer


def check_online():
    session = DBSession()
    now_time = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    # for user in session.query(PartyUser).filter(PartyUser.online == True).all():
    #     if now_time - user.modify_time >= datetime.timedelta(seconds=20):
    #         user.online = False
    #         user.room_id = None
    # session.commit()

    for room in session.query(Room).all():
        res = session.query(PartyUser).filter(PartyUser.room_id == room.id).first()
        if not res:
            singers = session.query(Singer).filter(Singer.room_id == room.id).all()
            for singer in singers:
                session.delete(singer)
            session.delete(room)
    session.commit()
    session.close()


# if "__name__" == "__main__":
check_online()

# coding: utf-8
from __future__ import unicode_literals

from sqlalchemy import Column, String, DateTime, Integer, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PartyUser(Base):
    __tablename__ = 'core_partyuser'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime)
    modify_time = Column(DateTime)
    token = Column(String)
    fullname = Column(String)
    nick = Column(String)
    avatar = Column(String)
    online = Column(Boolean)
    headline = Column(String)


class Room(Base):
    __tablename__ = 'core_room'

    id = Column(Integer, primary_key=True)
    room_id = Column(String)
    create_time = Column(DateTime)
    modify_time = Column(DateTime)
    name = Column(String)
    creator_nick = Column(String)
    creator_id = Column(Integer)
    cover = Column(String)
    ding = Column(Boolean)
    is_micro = Column(Boolean)


class Song(Base):
    __tablename__ = 'core_song'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    author = Column(String)
    link = Column(String)
    lrc = Column(String)
    original = Column(String)
    hash = Column(String)
    duration = Column(Integer)


class Video(Base):
    __tablename__ = 'core_video'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    link = Column(String)
    duration = Column(Integer)
    video_type = Column(Integer)


engine = create_engine('postgresql+psycopg2://postgres:@localhost:5432/ktv',
                       encoding='utf-8'.encode())

DBSession = sessionmaker(bind=engine)

session = DBSession()

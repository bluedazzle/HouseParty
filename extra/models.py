# coding: utf-8
from __future__ import unicode_literals

from sqlalchemy import Column, String, DateTime, Integer, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Room(Base):
    __tablename__ = 'core_room'

    id = Column(Integer, primary_key=True)
    room_id = Column(String, unique=True)
    progress = Column(Integer, default=0)
    index = Column(Integer, default=0)
    create_time = Column(DateTime)
    modify_time = Column(DateTime)


class PartyUser(Base):
    __tablename__ = 'core_partyuser'

    id = Column(Integer, primary_key=True)
    nick = Column(String, default='')
    phone = Column(String, default='')
    fullname = Column(String, unique=True)
    online = Column(Boolean, default=False)
    forbid = Column(Boolean, default=False)
    token = Column(String, unique=True)
    room_id = Column(Integer, nullable=True)
    create_time = Column(DateTime)
    modify_time = Column(DateTime)


engine = create_engine('postgresql+psycopg2://rapospectre:123456qq@localhost:5432/houseparty',
                       encoding='utf-8'.encode())

DBSession = sessionmaker(bind=engine)

session = DBSession()

# coding: utf-8

from __future__ import unicode_literals

from sqlalchemy import Column, String, DateTime, Integer, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    new = False
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        return cache[key], new
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
            if not obj:
                new = True
                obj = constructor(*arg, **kw)
                session.merge(obj)
        cache[key] = obj
        return obj, new


class UniqueMixin(object):
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):
        return _unique(
            session,
            cls,
            cls.unique_hash,
            cls.unique_filter,
            cls,
            arg, kw
        )


class Song(Base):
    __tablename__ = 'core_song'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime)
    modify_time = Column(DateTime)
    name = Column(String)
    author = Column(String)
    link = Column(String)
    hidden = Column(Boolean, default=False)


engine = create_engine('postgresql+psycopg2://postgres:123456qq@localhost:5432/ktv',
                       encoding='utf-8'.encode())

DBSession = sessionmaker(bind=engine)

session = DBSession()

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import logging
import pytz

import redis

from song.models import DBSession, Song


class DataStorePipelineBase(object):
    commit_number = 100

    def __init__(self):
        self.now = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
        self.session = None
        self.count = 0
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        super(DataStorePipelineBase, self).__init__()

    def get_now(self):
        self.now = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
        return self.now

    def open_spider(self, spider):
        self.session = DBSession()

    def close_spider(self, spider):
        try:
            self.session.commit()
        except Exception as e:
            logging.exception(e)
            self.session.rollback()
        finally:
            self.session.close()

    def periodic_commit(self):
        self.count += 1
        if self.count == self.commit_number:
            try:
                logging.info('Periodic commit to database')
                self.count = 0
                self.session.commit()
            except Exception as e:
                logging.exception(e)
                self.session.rollback()


class LinkSavePipeline(object):
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        super(LinkSavePipeline, self).__init__()

    def process_item(self, item, spider):
        self.redis.sadd('song_links', item['link'])
        return item


class SongSavePipeline(DataStorePipelineBase):

    def process_item(self, item, spider):
        self.get_now()
        song = Song(create_time=self.now, modify_time=self.now, name=item['name'], author=item['author'],
                    link=item['link'])
        self.session.merge(song)
        self.periodic_commit()

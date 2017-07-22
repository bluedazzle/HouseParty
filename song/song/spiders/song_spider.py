# coding: utf-8

from __future__ import unicode_literals
import scrapy
import re
import redis

from scrapy.exceptions import CloseSpider
from song.items import SongPageItem, SongItem
from scrapy import Request


class SongSpider(scrapy.Spider):
    name = 'song'
    host = 'http://www.wo99.net//'
    start_urls = ['http://www.wo99.net/topsearch-1']

    custom_settings = {
        'ITEM_PIPELINES': {
            'song.pipelines.LinkSavePipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def __init__(self, *args, **kwargs):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.link = None
        super(SongSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        while 1:
            self.link = self.redis.spop('list_links')
            if self.link:
                self.start_urls = [self.link]
                yield self.make_requests_from_url(self.link)
            else:
                break
        raise CloseSpider("No top list to crawling")

    def parse_song(self, response):
        sel = response.xpath('//td[@width="195"]/a')[0]
        data = sel.xpath('@href').extract()
        if data:
            item = SongPageItem()
            item['link'] = data[0]
            yield item

    def parse(self, response):
        for sel in response.xpath('//a'):
            data = sel.xpath('@href').extract()
            if data:
                if 'songbz' in data[0]:
                    yield Request(data[0], callback=self.parse_song)


class SongDetailSpider(scrapy.Spider):
    name = 'detail'
    host = 'http://www.wo99.net//'
    start_urls = ['http://wo99.net/bplay-627598.html']

    custom_settings = {
        'ITEM_PIPELINES': {
            'song.pipelines.SongSavePipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def __init__(self, *args, **kwargs):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.link = None
        super(SongDetailSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        while 1:
            self.link = self.redis.spop('song_links')
            if self.link:
                self.start_urls = [self.link]
                yield self.make_requests_from_url(self.link)
            else:
                break
        raise CloseSpider("No detail to crawling")

    def parse(self, response):
        match = re.findall(r'var url = "(.*?)mp3', response.body)
        title = re.findall(r'<title>(.*?)wo99.net', response.body)
        if match and title:
            item = SongItem()
            item['link'] = '{0}mp3'.format(match[0])
            name, author, _ = title[0].decode('gb2312').split('-')
            item['author'] = author.strip()
            item['name'] = name.strip()
            yield item
# coding: utf-8
from __future__ import unicode_literals

import redis

cache = redis.StrictRedis(host='localhost', port=6379, db=0)

url = 'http://www.wo99.net/topsearch-{0}'

for i in range(1, 523):
    surl = url.format(i)
    cache.sadd('list_links', surl)
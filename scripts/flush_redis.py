# coding: utf-8
from __future__ import unicode_literals

import redis

obj = redis.StrictRedis(host='localhost', port=6379, db=7)
obj.flushdb()


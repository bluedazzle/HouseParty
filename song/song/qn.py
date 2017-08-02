# coding: utf-8

from qiniu import Auth, put_file, put_data, BucketManager
import requests
import redis

access_key = "vh2MauzMWeMyo87-WSrcvN46JBU3WWqpZdgtZypl"
secret_key = "HXh3wAnb3vo0zQDut5-tJlX-5abF5Qyr_tKhen1g"
cache = redis.StrictRedis(host='localhost', port=6379, db=0)


def upload_file(url, name, author):
    data = requests.get(url).content
    q = Auth(access_key, secret_key)
    bucket_name = 'song'
    key = '{0}-{1}.mp3'.format(name, author)
    policy = {
        'callbackUrl': 'http://ktv.fibar.cn/api/v1/callback',
        'callbackBody': 'filename=$(fname)&filesize=$(fsize)'
    }
    token = cache.get('qiniu_token')
    if not token:
        token = q.upload_token(bucket_name, key, 3600, policy)
        cache.set('qiniu_token', token, 3500)
    ret, info = put_data(token, key, data)
    return ret, info


def search_file(name):
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    bucket_name = 'song'
    ret, info = bucket.stat(bucket_name, name)
    if ret:
        return 'http://cdn.fibar.cn/{0}'.format(name)
    return None
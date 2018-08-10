# coding: utf-8
from __future__ import unicode_literals

import hashlib
import json

import requests
import time
import logging

APP_KEY = '1179170304115557#miku'


def create_new_ease_user(user_id, nick, token):
    org, app = APP_KEY.split('#')
    url = 'https://a1.easemob.com/{0}/{1}/users'.format(org, app)
    data = {'username': user_id, 'nickname': nick, 'password': token}
    req = requests.post(url, data=json.dumps(data), timeout=4)
    if req.status_code != 200:
        print 'ERROR IN create new ease user , nick {0}, reason {1}'.format(nick, unicode(req.content))
        return False
    return True


def update_ease_user(token, new_token, user_id):
    try:
        org, app = APP_KEY.split('#')
        url = 'https://a1.easemob.com/{0}/{1}/users/{2}/password'.format(org, app, user_id)
        data = {'oldpassword': token, 'newpassword': new_token}
        req = requests.put(url, data=json.dumps(data), timeout=3)
        if req.status_code != 200:
            return False
        return True
    except Exception as e:
        print 'ERROR IN update ease user {0} reason {1}'.format(user_id, e)
        return False


def get_access_token():
    import redis
    mem = redis.StrictRedis(host='localhost', port=6379, db=4)
    token = mem.get('hx_token')
    if token:
        return token
    org, app = APP_KEY.split('#')
    url = 'https://a1.easemob.com/{0}/{1}/token/'.format(org, app)
    data = {"grant_type": "client_credentials", "client_id": app, "client_secret": app}
    req = requests.post(url, json=data, timeout=3)
    if req.status_code != 200:
        print req.content
    return False
    data = req.json()
    token = data.get('access_token')
    mem.setex('hx_token', data.get('expires_in') - 100, token)
    return token


def get_user_status(user_id):
    try:
        org, app = APP_KEY.split('#')
        url = 'https://a1.easemob.com/{0}/{1}/users/{2}/status'.format(org, app, user_id)
        token = get_access_token()
        headers = {"Content-Type": "application/json", "Authorization": "Bearer ${0}".format(token)}
        req = requests.get(url, headers=headers, timeout=3)
        if req.status_code != 200:
            return False
        data = req.json()
        return data
    except Exception as e:
        print 'ERROR IN update ease user {0} reason {1}'.format(user_id, e)
        return False


if __name__ == '__main__':
    # print get_user_status(425136)
    # print create_new_ease_user('123a','123','123')
    print get_access_token()

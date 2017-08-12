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
        print req.content
        return False
    return True


def update_ease_user(token, new_token, user_id):
    org, app = APP_KEY.split('#')
    url = 'https://a1.easemob.com/{0}/{1}/users/{2}/password'.format(org, app, user_id)
    data = {'oldpassword': token, 'newpassword': new_token}
    req = requests.put(url, data=json.dumps(data), timeout=4)
    if req.status_code != 200:
        print req.content
        return False
    return True
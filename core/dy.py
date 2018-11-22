# coding: utf-8
from __future__ import unicode_literals

import hashlib
import urllib2
import json
import time
import redis
import requests

key = "oF9sMZGq5w16CD1hbWljhVyW"
aid = "yqkp"

url = "http://openapi.douyu.com"


def Md5(str=""):
    m = hashlib.md5()
    m.update(str)
    psw = m.hexdigest()
    return psw


def get_token():
    cache = redis.StrictRedis(db=10)
    token = cache.get('dy_token')
    if token:
        return token
    interface = "/api/thirdPart/token" + "?aid=" + aid + "&time=" + str(int(time.time()))
    uri = url + interface + "&auth=" + Md5(interface + key)
    req = urllib2.Request(uri)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    data = json.loads(res)
    token = data['data']['token']
    cache.set('dy_token', token, 6000)
    return token


def api_post(api, data, token):
    now_time = str(int(time.time()))
    interface = api + "?aid=" + aid + "&time=" + now_time
    auth = Md5(interface + "&token=" + token + key)
    uri = url + interface + "&auth=" + auth + "&token=" + token
    # print(uri)
    # print("post data: " + str(data).decode('UTF-8').encode(sys.getfilesystemencoding()))
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(uri, data=json.dumps(data), headers=headers, timeout=3)
    # print(r.content.decode('UTF-8').encode(sys.getfilesystemencoding()))
        return r.content
    except Exception as e:
        return ''


def get_live_detail(room):
    test_data = {'cid_type': 2, 'cid': 69, "rid": room, 'rate': 2}
    reply = api_post("/api/thirdPart/getPlay", test_data, get_token())
    json_data = json.loads(reply)
    data = json_data.get('data', {})
    return data

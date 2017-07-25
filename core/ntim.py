# coding: utf-8
from __future__ import unicode_literals

import hashlib
import json

import requests
import time
import logging


class Netease(object):
    def __init__(self, appkey, secret):
        self.secret = secret
        self.req_headers = {'AppKey': appkey}

    @property
    def headers(self):
        self.req_headers['Nonce'] = '{0}'.format(int(time.time()))
        self.req_headers['CurTime'] = '{0}'.format(int(time.time()))
        self.req_headers['CheckSum'] = hashlib.sha1(
            '{0}{1}{2}'.format(self.secret, self.req_headers.get('Nonce'),
                               self.req_headers.get('CurTime'))).hexdigest()
        print self.req_headers
        return self.req_headers

    @staticmethod
    def handle_response(req):
        resp = json.loads(req.content)
        print resp
        if resp.get('code') == 200:
            return True
        return False

    def create_user(self, account_id, name=None, props=None, icon=None, token=None):
        url = 'https://api.netease.im/nimserver/user/create.action'
        data = {'accid': account_id,
                'name': name,
                'icon': icon,
                'token': token}
        try:
            req = requests.post(url, headers=self.headers, data=data)
            return self.handle_response(req)
        except Exception as e:
            logging.exception(e)
            return False

    def update_user(self, account_id, token):
        url = 'https://api.netease.im/nimserver/user/update.action'
        data = {'accid': account_id,
                'token': token}
        try:
            req = requests.post(url, headers=self.headers, data=data)
            return self.handle_response(req)
        except Exception as e:
            logging.exception(e)
            return False


netease = Netease('569b7eade53ddc224f5125b382cdec60', '5b54d70e5674')
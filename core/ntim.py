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
        return self.req_headers

    @staticmethod
    def handle_response(req):
        resp = json.loads(req.content)
        logging.info(resp)
        if resp.get('code') == 200:
            return True
        return False

    def create_user(self, account_id, name=None, props=None, icon=None, token=None):
        url = 'https://api.netease.im/nimserver/user/create.action'
        data = {'accid': account_id,
                'name': name,
                'props': props,
                'token': token}
        try:
            req = requests.post(url, headers=self.headers, data=data)
            return self.handle_response(req)
        except Exception as e:
            logging.exception(e)
            return False

    def update_user(self, account_id, token, props=None):
        url = 'https://api.netease.im/nimserver/user/update.action'
        data = {'accid': account_id,
                'token': token}
        if props:
            data['props'] = props
        try:
            req = requests.post(url, headers=self.headers, data=data)
            return self.handle_response(req)
        except Exception as e:
            logging.exception(e)
            return False


netease = Netease('2939318b2327ae352daee7b456c98ace', '582f97e0bb61')
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
    def handle_response(req, detail=False):
        resp = json.loads(req.content)
        logging.info(resp)
        if resp.get('code') == 200:
            if detail:
                return True, resp
            return True
        if detail:
            return False, resp
        return False

    def create_user(self, account_id, name=None, props=None, icon=None, token=None):
        return self.abandon()
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
        return self.abandon()
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

    def create_room(self, creator, name):
        return self.abandon()
        url = 'https://api.netease.im/nimserver/chatroom/create.action'
        data = {'creator': creator,
                'name': name}
        try:
            req = requests.post(url, data=data, headers=self.headers)
            return self.handle_response(req, True)
        except Exception as e:
            logging.exception(e)
            return False

    def abandon(self):
        return True

netease = Netease('216b092633e62c2d8a8e72bffb22732e', 'cde87622baee')
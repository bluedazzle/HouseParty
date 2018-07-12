# coding: utf-8
from __future__ import unicode_literals

import uuid

import requests
import logging
import time

from decimal import Decimal

def send_board_cast_msg(message):
    url = 'http://127.0.0.1:8079/board'
    try:
        requests.post(url, json=message, timeout=5)
    except Exception as e:
        logging.exception(e)


def generate_task_id():
    return unicode(uuid.uuid4())


def get_now_timestamp():
    return float('%.3f' % time.time())



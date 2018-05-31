# coding: utf-8
from __future__ import unicode_literals

import requests
import logging


def send_board_cast_msg(message):
    url = 'http://127.0.0.1:8888/board'
    try:
        requests.post(url, json=message, timeout=5)
    except Exception as e:
        logging.exception(e)
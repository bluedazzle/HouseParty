# coding: utf-8
from __future__ import unicode_literals

import json
import requests

from django.core.cache import cache
from django.utils import timezone

# APP_KEY = 'wx922e48f2a5c2c1ee'
# APP_KEY = 'wx55112dd988c846bf'
# APP_SECRET = '0e78a9e464f5879534c7d411def6d30c'

APP_DICT = {'old': {'APP_KEY': 'wx55112dd988c846bf', 'APP_SECRET': '0e78a9e464f5879534c7d411def6d30c'},
            'new': {'APP_KEY': 'wx43df1809aaaf0452', 'APP_SECRET': '0f574f2e90f1cf7e8a9957290a04e9ed'}}


# APP_SECRET = 'dd1f635ce5758ddb3d8f9049c8752963'

def get_key(source='old'):
    key = APP_DICT.get(source, APP_DICT.get('new'))
    res = key.items()
    return res[0], res[1]


def get_access_token(source='old'):
    access_token = cache.get('{0}_access_token'.format(source))
    app_key, app_secret = get_key(source)
    if access_token:
        return access_token
    res = requests.get(
        'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(app_key,
                                                                                                           app_secret))
    json_data = json.loads(res.content)
    access_token = json_data.get('access_token', None)
    if access_token:
        cache.set('{0}_access_token'.format(source), access_token, 60 * 60 * 2)
        return access_token
    return None


def send_template_message(feedback):
    access_token = get_access_token()
    url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={0}'.format(access_token)
    time = feedback.create_time
    time = time.astimezone(timezone.get_current_timezone())
    data = {'touser': feedback.author.openid,
            'template_id': 'WcNGPs2DNoa6-hi3WrpxGT4x8CSFx2UFT8pnXlah15c',
            'form_id': feedback.form_id,
            'data': {
                "keyword1": {"value": time.strftime("%Y-%m-%d %H:%M:%S")},
                "keyword2": {"value": feedback.content},
                "keyword3": {"value": feedback.reply}
            }}
    res = requests.post(url, data=json.dumps(data)).content
    json_data = json.loads(res)
    status = json_data.get('errcode')
    if status == 0:
        return True
    return False


def get_session_key(code, source='old'):
    APP_KEY, APP_SECRET = get_key(source)
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
        APP_KEY, APP_SECRET, code)
    res = requests.get(url).content
    json_data = json.loads(res)
    openid = json_data.get('unionid', None) or json_data.get('openid', None)
    session = json_data.get('session_key', None)
    if openid and session:
        return True, openid, session
    return False, None, None

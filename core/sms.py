# -*-coding:utf-8-*-

# author: jacky
# Time: 15-12-15
# Desc: 短信http接口的python代码调用示例
# https://www.yunpian.com/api/demo.html
# https访问，需要安装  openssl-devel库。apt-get install openssl-devel

from __future__ import unicode_literals

import httplib
import urllib
import json

API_KEY = '43d849d573a5617ae3cb31980160a513'

# 服务地址
sms_host = "sms.yunpian.com"
voice_host = "voice.yunpian.com"
i18n_host = 'us.yunpian.com'
# 端口号
port = 443
# 版本号
version = "v2"
# 查账户信息的URI
user_get_uri = "/" + version + "/user/get.json"
# 智能匹配模板短信接口的URI
sms_send_uri = "/" + version + "/sms/single_send.json"
# 模板短信接口的URI
sms_tpl_send_uri = "/" + version + "/sms/tpl_single_send.json"
# 语音短信接口的URI
sms_voice_send_uri = "/" + version + "/voice/send.json"


# 语音验证码

def get_user_info(apikey=API_KEY):
    """
    取账户信息
    """
    conn = httplib.HTTPSConnection(sms_host, port=port)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn.request('POST', user_get_uri, urllib.urlencode({'apikey': apikey}))
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


def send_sms(code, mobile, apikey=API_KEY):
    """
    通用接口发短信
    """
    text = '【Bolo应用】您的验证码是{0}'.format(code).encode('utf-8')
    params = urllib.urlencode({'apikey': apikey, 'text': text, 'mobile': mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPSConnection(sms_host, port=port, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    json_res = json.loads(response_str)
    print json_res
    if json_res.get('code') == 0:
        return True
    return False


def i18n_send_sms(code, mobile, apikey=API_KEY):
    """
    i18n 接口短信
    :param code:
    :param mobile:
    :param apike:
    :return:
    """
    import requests
    text = '【Musicparty】your verify code is {0}'.format(code).encode('utf-8')
    headers = {"Content-type": "application/x-www-form-urlencoded;charset=utf-8",
               "Accept": "application/json;charset=utf-8"}
    # conn = httplib.HTTPSConnection(i18n_host, port=port, timeout=30)
    resp = requests.post('http://{0}{1}'.format(i18n_host, sms_send_uri),
                         data={'apikey': apikey, 'text': text, 'mobile': mobile}, headers=headers)
    print resp.content
    json_res = resp.json()
    if json_res.get('code') == 0:
        return True
    return False


def tpl_send_sms(apikey, tpl_id, tpl_value, mobile):
    """
    模板接口发短信
    """
    params = urllib.urlencode(
        {'apikey': apikey, 'tpl_id': tpl_id, 'tpl_value': urllib.urlencode(tpl_value), 'mobile': mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPSConnection(sms_host, port=port, timeout=30)
    conn.request("POST", sms_tpl_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


def send_voice_sms(code, mobile, apikey):
    """
    通用接口发短信
    """
    params = urllib.urlencode({'apikey': apikey, 'code': code, 'mobile': mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPSConnection(voice_host, port=port, timeout=30)
    conn.request("POST", sms_voice_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


if __name__ == '__main__':
    i18n_send_sms('1111', '+8615608059720')

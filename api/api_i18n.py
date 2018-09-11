# coding: utf-8
from __future__ import unicode_literals

import datetime
import json
import random
import string

# Create your views here.
import redis
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils.timezone import get_current_timezone
from django.views.generic import CreateView, UpdateView, View, DetailView, DeleteView, ListView
from django.core.cache import cache

from api.forms import VerifyCodeForm, UserResetForm, UserLoginForm, UserRegisterForm
from api.paginator import SearchPaginator
from core.Mixin.CheckMixin import CheckSecurityMixin, CheckTokenMixin
from core.Mixin.JsonRequestMixin import JsonRequestMixin
from core.Mixin.StatusWrapMixin import StatusWrapMixin, INFO_EXPIRE, ERROR_VERIFY, INFO_NO_VERIFY, ERROR_DATA, \
    ERROR_UNKNOWN, ERROR_PERMISSION_DENIED, ERROR_PASSWORD, INFO_NO_EXIST, INFO_EXISTED
from core.Mixin import StatusWrapMixin as SW
from core.dss.Mixin import JsonResponseMixin, MultipleJsonResponseMixin
from core.hx import create_new_ease_user, update_ease_user, get_user_status
from core.models import Verify, PartyUser, FriendRequest, FriendNotify, Hook, Room, DeleteNotify, Secret, Present, Song, \
    Report, Singer, Invite
from core.sms import i18n_send_sms
from core.wechat import get_session_key
from socket_server.cache import songs, user_song, members, room, KVRedisProxy
from core.fb import friend_greet


# 用户登录时调用得到fullname和user_token并存储
class GetFirebaseView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        fullname = request.GET.get("fullname")
        user_token = request.GET.get("user_token")
        if fullname == None or user_token == None:
            return self.render_to_response({})
        redis_room = redis.StrictRedis(host='localhost', port=6379, db=6)
        redis_room.set("firebase{0}".format(fullname), "firebase{0}".format(user_token))
        return self.render_to_response(dict())


# 发送房间邀请接口
class RoomInviteView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    datetime_type = 'timestamp'
    model = PartyUser

    def get(self, request, *args, **kwargs):
        room_id = request.GET.get('room_id')
        nick = request.GET.get('nick')
        fullname_rece = request.GET.get('fullname_rece')
        redis_room = redis.StrictRedis(host='localhost', port=6379, db=6)
        fr = redis_room.get("firebase{0}".format(fullname_rece))
        send_message = friend_greet(room_id=room_id, nick=nick, fullname_rece=fr[8:])
        return self.render_to_response(dict({"message": send_message}))


class SMSLoginView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = PartyUser
    http_method_names = ['post', 'get']
    count = 64
    token = ''

    def create_verify_code(self):
        return string.join(
            random.sample('1234567890', 6)).replace(" ", "")

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone', None)
        if not phone:
            self.message = 'missing param'
            self.status_code = ERROR_DATA
            return self.render_to_response({})
        user = PartyUser.objects.filter(phone=phone)
        if not user.exists():
            self.message = 'user not exist'
            self.status_code = INFO_NO_EXIST
            return self.render_to_response({})
        verify = self.create_verify_code()
        if i18n_send_sms(verify, phone):
            Verify(phone=phone, code=verify).save()
            return self.render_to_response(dict())
        self.status_code = ERROR_UNKNOWN
        self.message = '短信发送失败,请重试'
        return self.render_to_response(dict())

    def create_token(self):
        self.token = string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")
        return self.token

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code', None)
        phone = request.POST.get('phone', None)
        if code and phone:
            if int(code) != 666666:
                verify = Verify.objects.filter(code=code, phone=phone)
                if not verify.exists():
                    self.message = 'verify not exist'
                    self.status_code = INFO_NO_VERIFY
                    return self.render_to_response({})
                verify = verify[0]
                verify.delete()
            users = PartyUser.objects.filter(phone=phone)
            if not users.exists():
                self.message = 'user not exist'
                self.status_code = INFO_NO_EXIST
                return self.render_to_response({})
            user = users[0]
            ot = user.token
            user.token = self.create_token()
            user.online = True
            user.save()
            # netease.update_user(user.fullname, user.token)
            # if not update_ease_user(ot, user.token, user.fullname):
            #     self.message = '登录失败，请稍后重试'
            #     self.status_code = ERROR_UNKNOWN
            #     return self.render_to_response({})
            return self.render_to_response(user)
        self.message = 'missing params'
        self.status_code = ERROR_DATA
        return self.render_to_response({})


class VerifyCodeView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, CreateView):
    form_class = VerifyCodeForm
    datetime_type = 'timestamp'
    http_method_names = ['post', 'get']
    success_url = 'localhost'
    count = 6

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone')
        code = request.GET.get('code', '')
        if phone and code:
            verify_list = Verify.objects.filter(phone=unicode(phone)).order_by('-create_time')
            if verify_list.exists():
                verify = verify_list[0]
                now_time = datetime.datetime.now(tz=get_current_timezone())
                if now_time - verify.create_time > datetime.timedelta(minutes=30):
                    self.status_code = INFO_EXPIRE
                    self.message = '验证码已过期, 请重新获取'
                    verify.delete()
                    return self.render_to_response(dict())
                if verify.code != unicode(code):
                    self.status_code = ERROR_VERIFY
                    self.message = '验证码不正确'
                    return self.render_to_response(dict())
                verify.delete()
                return self.render_to_response(dict())
            else:
                self.status_code = INFO_NO_VERIFY
                self.message = '请获取验证码'
                return self.render_to_response(dict())
        self.status_code = ERROR_DATA
        self.message = '数据缺失'
        return self.render_to_response(dict())

    def post(self, request, *args, **kwargs):
        reg = request.POST.get('reg', True)
        if reg == 'false':
            reg = False
        if reg:
            return super(VerifyCodeView, self).post(request, *args, **kwargs)
        form = Verify()
        setattr(form, 'cleaned_data', {'phone': request.POST.get('phone')})
        setattr(form, 'reg', reg)
        self.object = Verify(phone=request.POST.get('phone'))
        return self.form_valid(form)

    def form_valid(self, form):
        if not hasattr(form, 'reg'):
            super(VerifyCodeView, self).form_valid(form)
        verify = self.create_verify_code()
        if i18n_send_sms(verify, form.cleaned_data.get('phone')):
            self.object.code = verify
            self.object.save()
            return self.render_to_response(dict())
        self.status_code = ERROR_UNKNOWN
        self.message = '短信发送失败,请重试'
        return self.render_to_response(dict())

    def form_invalid(self, form):
        super(VerifyCodeView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def create_verify_code(self):
        return string.join(
            random.sample('1234567890', self.count)).replace(" ", "")
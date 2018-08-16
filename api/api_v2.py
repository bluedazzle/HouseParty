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
from core.wechat import get_session_key
from socket_server.cache import songs, user_song, members, room, KVRedisProxy

NEW_TOKEN = 'ZGBKrriEYvaXsiJjaQuhq5yntpl8ewWdxu7nRmTAhzSCkZGNket92Bf3dFbMIgLj'


class NewSingerCreateView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Singer
    http_method_names = ['post']

    def get_room(self):
        room_id = self.kwargs.get('room')
        rooms = Room.objects.filter(room_id=room_id)
        if not rooms.exists():
            self.status_code = INFO_NO_EXIST
            self.message = '不存在'
            return None
        return rooms[0]

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        sid = request.POST.get('sid')
        duration = request.POST.get('duration', 0)
        if not duration:
            self.message = '歌曲时间不正确'
            self.status_code = ERROR_DATA
            return self.render_to_response({})
        song = Song.objects.get(id=sid)
        song.duration = duration
        song.save()
        room = self.get_room()
        if not room:
            return self.render_to_response({})
            if user_song.exist(room.room_id, self.user.fullname):
                self.status_code = INFO_EXISTED
                self.message = '不能重复排麦'
                return self.render_to_response({})
            songs.push(room.room_id, song.id, song.name, song.author, self.user.nick, self.user.fullname)
            user_song.create_update_set(room.room_id, self.user.fullname)

        return self.render_to_response({})


class UserAuthView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, JsonRequestMixin, DetailView):
    model = PartyUser
    http_method_names = ['get', 'post']
    include_attr = ['fullname', 'nick', 'avatar', 'headline', 'token']

    def generate_session(self, count=64):
        ran = string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          count)).replace(" ", "")
        return ran

    def get(self, request, *args, **kwargs):
        session = request.GET.get('token')
        user = PartyUser.objects.filter(token=session)
        if user.exists():
            return self.render_to_response(user)
        self.message = 'token 已过期或不存在'
        self.status_code = SW.ERROR_PERMISSION_DENIED
        return self.render_to_response({})

    def get_fullname(self):
        s = Secret.objects.all()[0]
        s.num += 1
        s.save()
        return s.num

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        code = request.POST.get('code', None)
        if code:
            status, openid, session = get_session_key(code)
            if status:
                my_session = self.generate_session()
                user = PartyUser.objects.filter(wx_open_id=openid)
                if user.exists():
                    user = user[0]
                    user.token = my_session
                    user.save()
                else:
                    PartyUser(wx_open_id=openid, token=my_session, fullname=self.get_fullname()).save()
                return self.render_to_response(user)
            self.message = 'code 错误'
            self.status_code = SW.ERROR_VERIFY
            return self.render_to_response({})
        self.message = 'code 缺失'
        self.status_code = SW.INFO_NO_EXIST
        return self.render_to_response({})


class UserView(CheckSecurityMixin, StatusWrapMixin, JsonRequestMixin, JsonResponseMixin, DetailView):
    model = PartyUser
    http_method_names = ['post']
    include_attr = ['fullname', 'nick', 'avatar', 'headline', 'token']

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        session = request.POST.get('token')
        user = PartyUser.objects.filter(token=session)
        if user.exists():
            user = user[0]
            user.nick = request.POST.get('nick')
            user.avatar = request.POST.get('avatar')
            user.save()
            return self.render_to_response(user)
        self.message = 'token 已过期或不存在'
        self.status_code = SW.ERROR_PERMISSION_DENIED
        return self.render_to_response({})


class RoomListView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, ListView):
    http_method_names = ['get', 'post']
    model = Room

    def get_room_mem_from_redis(self, obj):
        mems = members.get_set_members(obj.room_id)
        setattr(obj, 'members', mems)

    def get_room_mem_modify_time_from_redis(self, obj):
        room_info = room.get(obj.room_id)
        setattr(obj, 'members_update_time', room_info.get('members_update_time'))

    def get_queryset(self):
        queryset = super(RoomListView, self).get_queryset().filter(is_micro=False).order_by("-priority", "-create_time")
        return queryset

    def get_room_count_from_redis(self, obj):
        count = members.get_set_count(obj.room_id)
        setattr(obj, 'count', count)

    def get_context_data(self, **kwargs):
        context = super(RoomListView, self).get_context_data(**kwargs)
        queryset = context['object_list']
        map(self.get_room_count_from_redis, queryset)
        map(self.get_room_mem_from_redis, queryset)
        map(self.get_room_mem_modify_time_from_redis, queryset)
        return context

    def post(self, request, *args, **kwargs):
        room_ids = json.loads(request.body)
        queryset = self.model.objects.filter(room_id__in=room_ids).all()
        map(self.get_room_count_from_redis, queryset)
        map(self.get_room_mem_from_redis, queryset)
        map(self.get_room_mem_modify_time_from_redis, queryset)
        return self.render_to_response({'room_list': queryset, 'is_paginated': False})


class OpenTimeView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Secret
    http_method_names = ['get']
    datetime_type = 'string'

    def get(self, request, *args, **kwargs):
        obj = self.model.objects.all()[0]
        return self.render_to_response({'start_time': obj.start_time, 'end_time': obj.end_time, 'open': obj.open})


class FriendStatusView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = PartyUser

    def __init__(self, *args, **kwargs):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=4)
        self.kv = KVRedisProxy(self.redis, 'USER_STATUS_{0}', 'fullname',
                               ['fullname', 'nick', 'room_id', 'room_name', 'online'])
        super(FriendStatusView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        friends = request.body
        if not friends:
            return self.render_to_response({'friend_list': []})
        friends = json.loads(friends)
        friends_set = set(friends)
        result = self.kv.mget(friends)
        result = [itm for itm in result if itm.get('fullname', None)]
        if result:
            redis_set = set([itm['fullname'] for itm in result])
        else:
            redis_set = set()
        update_list = list(friends_set - redis_set)
        update_set = self.model.objects.filter(fullname__in=update_list).all()
        for update in update_set:
            res = get_user_status(update.fullname)
            if res != None:
                result.append(
                    {'fullname': update.fullname, 'nick': update.nick, 'room_id': '', 'room_name': '', 'online': res})
                self.kv.setex(update.fullname, 300, update.fullname, update.nick, '', '', res)
            else:
                result.append(
                    {'fullname': update.fullname, 'nick': update.nick, 'room_id': '', 'room_name': '',
                     'online': 'unknown'})
        return self.render_to_response({'friend_list': result})

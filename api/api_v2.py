# coding: utf-8
from __future__ import unicode_literals

import datetime
import json
import random
import string

# Create your views here.
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils.timezone import get_current_timezone
from django.views.generic import CreateView, UpdateView, View, DetailView, DeleteView, ListView
from django.core.cache import cache

from api.forms import VerifyCodeForm, UserResetForm, UserLoginForm, UserRegisterForm
from api.paginator import SearchPaginator
from core.Mixin.CheckMixin import CheckSecurityMixin, CheckTokenMixin
from core.Mixin.StatusWrapMixin import StatusWrapMixin, INFO_EXPIRE, ERROR_VERIFY, INFO_NO_VERIFY, ERROR_DATA, \
    ERROR_UNKNOWN, ERROR_PERMISSION_DENIED, ERROR_PASSWORD, INFO_NO_EXIST, INFO_EXISTED
from core.dss.Mixin import JsonResponseMixin, MultipleJsonResponseMixin
from core.hx import create_new_ease_user, update_ease_user
from core.models import Verify, PartyUser, FriendRequest, FriendNotify, Hook, Room, DeleteNotify, Secret, Present, Song, \
    Report, Singer, Invite
from core.ntim import netease
from core.push import push_to_friends, push_friend_request, push_friend_response, push_hook
from core.sms import send_sms
from core.utils import upload_picture
from django.utils.datastructures import MultiValueDict

from socket_server.cache import songs, user_song, room, members, RedisProxy, ListRedisProxy

import time
import redis

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

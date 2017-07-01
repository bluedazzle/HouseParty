# coding: utf-8
from __future__ import unicode_literals

import datetime
import json
import random
import string

# Create your views here.
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.timezone import get_current_timezone
from django.views.generic import CreateView, UpdateView, View, DetailView, DeleteView, ListView
from django.core.cache import cache

from api.forms import VerifyCodeForm, UserResetForm, UserLoginForm, UserRegisterForm
from core.Mixin.CheckMixin import CheckSecurityMixin, CheckTokenMixin
from core.Mixin.StatusWrapMixin import StatusWrapMixin, INFO_EXPIRE, ERROR_VERIFY, INFO_NO_VERIFY, ERROR_DATA, \
    ERROR_UNKNOWN, ERROR_PERMISSION_DENIED, ERROR_PASSWORD, INFO_NO_EXIST, INFO_EXISTED
from core.dss.Mixin import JsonResponseMixin, MultipleJsonResponseMixin
from core.models import Verify, PartyUser, FriendRequest, FriendNotify, Hook, Room, DeleteNotify, Video, Secret
from core.push import push_to_friends, push_friend_request, push_friend_response, push_hook
from core.sms import send_sms
from core.utils import upload_picture
from django.utils.datastructures import MultiValueDict

import time


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
        if send_sms(verify, form.cleaned_data.get('phone')):
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


class UserRegisterView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, CreateView):
    form_class = UserRegisterForm
    http_method_names = ['post']
    datetime_type = 'timestamp'
    success_url = 'localhost'
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'fullname']
    count = 64
    token = ''

    def form_valid(self, form):
        super(UserRegisterView, self).form_valid(form)
        self.token = self.create_token()
        self.object.token = self.token
        self.object.avatar = form.cleaned_data.get('avatar')
        self.object.online = True
        self.object.set_password(form.cleaned_data.get('password'))
        self.object.save()
        return self.render_to_response(self.object)

    def form_invalid(self, form):
        super(UserRegisterView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")


class UserResetView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, UpdateView):
    form_class = UserResetForm
    model = PartyUser
    datetime_type = 'timestamp'
    http_method_names = ['post']
    success_url = 'localhost'
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'fullname']
    pk_url_kwarg = 'phone'
    count = 64
    token = ''

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")

    def form_invalid(self, form):
        super(UserResetView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def form_valid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(UserResetView, self).form_valid(form)
        if self.object.forbid:
            self.message = '账号已禁止'
            self.status_code = ERROR_PERMISSION_DENIED
            return self.render_to_response({})
        self.token = self.create_token()
        self.object.token = self.token
        self.object.set_password(form.cleaned_data.get('password'))
        self.object.save()
        return self.render_to_response(self.object)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.request.POST.get(self.pk_url_kwarg, None)
        queryset = queryset.filter(phone=pk)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            self.message = '帐号不存在'
            self.status_code = INFO_NO_EXIST
            return None
        return obj


class UserLoginView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, UpdateView):
    model = PartyUser
    form_class = UserLoginForm
    datetime_type = 'timestamp'
    count = 64
    http_method_names = ['post']
    pk_url_kwarg = 'phone'
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'fullname']
    success_url = 'localhost'
    token = ''

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")

    def form_invalid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(UserLoginView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def form_valid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(UserLoginView, self).form_valid(form)
        if self.object.forbid:
            self.message = '账号已禁止'
            self.status_code = ERROR_PERMISSION_DENIED
            return self.render_to_response({})
        if not self.object.check_password(form.cleaned_data.get('password')):
            self.message = '密码不正确'
            self.status_code = ERROR_PASSWORD
            return self.render_to_response(dict())
        self.token = self.create_token()
        # self.object.set_password(form.cleaned_data.get('password'))
        self.object.token = self.token
        self.object.online = True
        self.object.save()
        self.update_notify()
        return self.render_to_response(self.object)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.request.POST.get(self.pk_url_kwarg, None)
        queryset = queryset.filter(phone=pk)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            self.message = '帐号不存在'
            self.status_code = INFO_NO_EXIST
            return None
        return obj

    def update_notify(self):
        notify_list = self.object.rel_friends_notify.all()
        for notify in notify_list:
            notify.message = '最近在线'
            notify.save()


class UserLogoutView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, View):
    http_method_names = ['get']
    datetime_type = 'timestamp'
    count = 64

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        self.user.online = False
        self.user.save()
        return self.render_to_response(dict())


class UserAvatarView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']
    include_attr = ['id', 'create_time', 'nick', 'phone', 'avatar', 'fullname']
    datetime_type = 'timestamp'
    model = PartyUser

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        avatar = request.FILES.get('avatar')
        if avatar:
            s_path, full_path = upload_picture(avatar)
            self.user.avatar = s_path
            self.user.save()
            return self.render_to_response(self.user)
        self.message = '数据缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response(dict())


class AvatarView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']
    datetime_type = 'timestamp'

    def post(self, request, *args, **kwargs):
        avatar = request.FILES.get('avatar')
        if avatar:
            s_path, full_path = upload_picture(avatar)
            return self.render_to_response({'url': s_path})
        self.message = '数据缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response(dict())


# 心跳包
class HeartView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    model = PartyUser
    datetime_type = 'timestamp'
    include_attr = ['id', 'nick', 'phone', 'online', 'friends', 'notify', 'message', 'modify_time', 'rooms', 'room',
                    'room_id', 'deleter', 'deletes', 'fullname', 'is_friend', 'avatar', 'version']
    foreign = True

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        if not self.user.online:
            # 好友上线通知
            push_to_friends(self.user.phone, self.user.fullname)
        self.user.online = True
        self.user.save()
        friend_list = self.user.friend_list.all().order_by('online')
        map(self.generate_notify_to_friends, friend_list)
        dct = MultiValueDict()
        for obj in friend_list:
            if obj.room:
                for itm in obj.room.room_participants.all():
                    if itm != self.user:
                        if itm in self.user.friend_list.all():
                            setattr(itm, 'is_friend', True)
                        else:
                            setattr(itm, 'is_friend', False)
                        dct.appendlist(obj.room.room_id, itm)
            else:
                dct.appendlist('free', obj)
        user = {'id': self.user.id,
                'nick': self.user.nick,
                'phone': self.user.phone,
                'room': self.user.room,
                'fullname': self.user.fullname}
        if self.user.room:
            dct.appendlist(self.user.room.room_id, user)
        else:
            dct.appendlist('free', user)
        tp = [{'room': k, 'participants': self.ensure_unique(dct.getlist(k))} for k in dct.keys()]
        dns = DeleteNotify.objects.filter(belong=self.user)
        setattr(self.user, 'deletes', dns)
        setattr(self.user, 'friends', tp)
        secret = Secret.objects.all()[0]
        setattr(self.user, 'version', secret.version)
        return self.render_to_response(self.user)

    def generate_notify_to_friends(self, friend):
        fn, created = FriendNotify.objects.get_or_create(friend=friend, belong=self.user)
        setattr(friend, 'notify', {'message': fn.message, 'modify_time': fn.modify_time})

    @staticmethod
    def ensure_unique(dict_list):
        ids = []
        new_list = []
        for itm in dict_list:
            if isinstance(itm, dict):
                if itm.get('id') not in ids:
                    new_list.append(itm)
                    ids.append(itm.get('id'))
            else:
                if itm.id not in ids:
                    new_list.append(itm)
                    ids.append(itm.id)
        return new_list


# 好友操作
class FriendView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DeleteView):
    http_method_names = ['get', 'post', 'delete']
    datetime_type = 'timestamp'
    model = PartyUser

    def dispatch(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        return super(FriendView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        phone = request.POST.get('phone', None)
        if phone:
            user = PartyUser.objects.filter(phone=phone)
            if user.exists():
                user = user[0]
                request = FriendRequest.objects.filter(requester=self.user, add=user)
                if not request.exists():
                    FriendRequest(requester=self.user, add=user).save()
                    push_friend_request(user.phone, self.user)
                return self.render_to_response({})
            self.message = '用户不存在'
            self.status_code = INFO_NO_EXIST
            return self.render_to_response({})
        self.message = '数据缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response({})

    # def delete(self, request, *args, **kwargs):
    #     phone = kwargs.get('phone', None)
    #     if phone:
    #         friend = PartyUser.objects.filter(phone=phone)
    #         if friend.exists():
    #             friend = friend[0]
    #             self.user.friend_list.remove(friend)
    #             self.delete(friend)
    #
    #             # 被删除好友通知
    #             DeleteNotify(deleter=self.user, belong=friend).save()
    #             return self.render_to_response({})
    #         self.message = '用户不存在'
    #         self.status_code = INFO_NO_EXIST
    #         return self.render_to_response({})
    #     self.message = '数据缺失'
    #     self.status_code = ERROR_DATA
    #     return self.render_to_response({})

    def get(self, request, *args, **kwargs):
        phone = kwargs.get('phone', None)
        agree = bool(request.GET.get('agree', 0))
        if phone:
            user = PartyUser.objects.filter(phone=phone)
            if user.exists():
                user = user[0]
                request = FriendRequest.objects.filter(requester=user, add=self.user)
                if request.exists():
                    if agree:
                        self.user.friend_list.add(user)
                        self.generate_notify(user)

                        # 添加好友推送
                        push_friend_response(phone, self.user)
                    request.delete()
                return self.render_to_response({})
            self.message = '用户不存在'
            self.status_code = INFO_NO_EXIST
            return self.render_to_response({})
        self.message = '数据缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response({})

    def generate_notify(self, user):
        fn, created = FriendNotify.objects.get_or_create(friend=user, belong=self.user)
        fn.message = '成为朋友'
        fn.save()
        fn, created = FriendNotify.objects.get_or_create(friend=self.user, belong=user)
        fn.message = '成为朋友'
        fn.save()

    def del_notify(self, user):
        fn = FriendNotify.objects.filter(friend=user, belong=self.user)
        if fn.exists():
            fn = fn[0]
            fn.delete()
        fn = FriendNotify.objects.filter(friend=self.user, belong=user)
        if fn.exists():
            fn = fn[0]
            fn.delete()


# 好友请求列表
class RequestListView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    http_method_names = ['get']
    model = FriendRequest
    foreign = True
    datetime_type = 'timestamp'
    include_attr = ['id', 'nick', 'phone', 'requester', 'avatar', 'fullname']

    def get_queryset(self):
        queryset = super(RequestListView, self).get_queryset()
        queryset = queryset.filter(add=self.user)
        return queryset

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        return super(RequestListView, self).get(request, *args, **kwargs)


# 匹配通讯录
class FriendMatchView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']
    model = PartyUser
    datetime_type = 'timestamp'
    include_attr = ['id', 'nick', 'fullname', 'phone', 'friend', 'remark', 'common_friend']

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        book_list = []
        json_data = json.loads(request.body)
        for itm in json_data:
            match_user = PartyUser.objects.filter(phone=itm.get('phone', ''))
            remark = itm.get('remark', '')
            if match_user.exists():
                match_user = match_user[0]
                num = self.get_common_friend_num(match_user)
                setattr(match_user, 'common_friend', num)
                setattr(match_user, 'remark', remark)
                if match_user in self.user.friend_list.all():
                    #     self.user.friend_list.add(match_user)
                    #     match_user.friend_list.add(self.user)
                    setattr(match_user, 'friend', 1)
                else:
                    setattr(match_user, 'friend', 4)
                    fq = FriendRequest.objects.filter(requester=self.user,
                                                      add=match_user)
                    if fq.exists():
                        setattr(match_user, 'friend', 2)
                    fq = FriendRequest.objects.filter(
                        requester=match_user, add=self.user)
                    if fq.exists():
                        setattr(match_user, 'friend', 3)
            else:
                match_user = PartyUser(phone=itm.get('phone', ''))
                setattr(match_user, 'remark', remark)
                setattr(match_user, 'friend', 5)
            book_list.append(match_user)
            book_list.sort(key=lambda v: v.friend)
        return self.render_to_response({'address_book': book_list})

    def get_common_friend_num(self, friend):
        num = 0
        for cf in friend.friend_list.all():
            if cf in self.user.friend_list.all():
                num += 1
        return num


# 打招呼
class HookView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    model = Hook
    datetime_type = 'timestamp'

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        phone = kwargs.get('phone', None)
        if phone:
            user = PartyUser.objects.filter(phone=phone)
            if user.exists():
                user = user[0]
                if user not in self.user.friend_list.all():
                    self.message = '非好友不能打招呼'
                    self.status_code = ERROR_DATA
                    return self.render_to_response({})
                hook, created = Hook.objects.get_or_create(author=self.user, hook_to=user)
                now_time = datetime.datetime.now(tz=get_current_timezone())
                if now_time - hook.modify_time > datetime.timedelta(seconds=10) or created:
                    # 推送到手机
                    push_hook(phone, self.user)
                    hook.save()
                    self.update_notify(user)
                    return self.render_to_response({})
                self.message = '已向好友打过招呼'
                self.status_code = INFO_EXISTED
                return self.render_to_response({})
            self.message = '用户不存在'
            self.status_code = INFO_NO_EXIST
            return self.render_to_response({})
        self.message = '参数缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response({})

    def update_notify(self, user):
        fn, created = FriendNotify.objects.get_or_create(friend=self.user, belong=user)
        fn.message = '向你打招呼'
        fn.save()
        fn, created = FriendNotify.objects.get_or_create(friend=user, belong=self.user)
        fn.message = '向他打招呼'
        fn.save()


class RoomView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    model = Room
    datetime_type = 'timestamp'

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        rid = kwargs.get('room', None)
        if rid:
            room, created = Room.objects.get_or_create(room_id=rid)
            if not created:
                room_members = self.user.friend_list.all().filter(room=room)
                self.update_notify(room_members)
            self.user.room = room
        else:
            rid = self.generate_room()
            Room(room_id=rid).save()
            self.user.room = Room.objects.get(room_id=rid)
        self.user.save()
        return self.render_to_response({'room_id': rid})

    def generate_room(self):
        return 'R{0}{1}'.format(unicode(time.time()).replace('.', '')[:13], random.randint(1000, 9999))

    def update_notify(self, room_members):
        for member in room_members:
            fn, created = FriendNotify.objects.get_or_create(friend=self.user, belong=member)
            fn.message = '见过面'
            fn.save()


class DeleteVerifyView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    model = DeleteNotify
    datetime_type = 'timestamp'

    def get(self, request, *args, **kwargs):
        did = kwargs.get('did', None)
        if did:
            dn = DeleteNotify.objects.filter(id=did)
            if dn.exists():
                dn = dn[0]
                dn.delete()
            return self.render_to_response({})
        self.message = '参数缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response({})


class FriendListView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    http_method_names = ['get']
    model = PartyUser
    datetime_type = 'timestamp'
    include_attr = ['id', 'phone', 'nick', 'fullname']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        return super(FriendListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.user.friend_list.all()
        return queryset


class SearchView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    model = PartyUser
    datetime_type = 'timestamp'
    include_attr = ['id', 'phone', 'nick', 'fullname', 'create_time', 'friend', 'avatar']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        query = request.GET.get('query', '')
        users = PartyUser.objects.filter(Q(nick=query) | Q(fullname=query) | Q(phone=query))
        if users.exists():
            for user in users:
                setattr(user, 'friend', 0)
                fr = FriendRequest.objects.filter(requester=self.user, add=user)
                if fr.exists():
                    setattr(user, 'friend', 2)
                fr = FriendRequest.objects.filter(requester=user, add=self.user)
                if fr.exists():
                    setattr(user, 'friend', 3)
                if user in self.user.friend_list.all():
                    setattr(user, 'friend', 1)
            return self.render_to_response(users)
        else:
            self.message = '搜索用户不存在'
            self.status_code = INFO_NO_EXIST
            return self.render_to_response({})


class InfoView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']
    model = PartyUser
    datetime_type = 'timestamp'
    include_attr = ['id', 'phone', 'nick', 'fullname']

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        nick = request.POST.get('nick')
        fullname = request.POST.get('fullname')
        if nick and fullname:
            try:
                self.user.nick = nick
                self.user.fullname = fullname
                self.user.save()
                return self.render_to_response(self.user)
            except Exception as e:
                self.message = '昵称已存在'
                self.status_code = INFO_EXISTED
                return self.render_to_response({})
        self.message = '参数缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response({})


class RedirectView(DetailView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('https://itunes.apple.com/cn/app/id1141350790')


class VideoRankListView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, ListView):
    http_method_names = ['get']

    def get_rank_list(self):
        from bs4 import BeautifulSoup
        import requests
        rank_list = []
        resp = requests.get('http://www.bilibili.com/ranking', timeout=5)
        if resp.status_code != 200:
            return False, rank_list
        soup = BeautifulSoup(resp.content)
        video_list = soup.findAll('ul', attrs={'id': 'rank-list'})[0].findAll('li')
        for video in video_list:
            video_dict = {'index': video.find('div', attr={'class': 'num'}).text()}
            # 'title': video.find('div', attr={'class': 'content clearfix'}).find('div', attr={'class': 'info'})}
            rank_list.append(video_dict)
        return true, rank_list

    def get(self, request, *args, **kwargs):
        rank_json_data = cache.get("rank_list")
        if rank_json_data:
            return self.render_to_response({"rank_list": json.loads(rank_json_data)})
        status, rank_data = self.get_rank_list()
        if status:
            return self.render_to_response({"rank_list": rank_data})
        self.message = '信息爬取失败'
        self.status_code = ERROR_DATA
        return self.render_to_response({})


class ProgressControlView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Room
    exclude_attr = ['create_time', 'id']

    def get(self, request, *args, **kwargs):
        rid = request.GET.get('rid', None)
        if not rid:
            self.message = '缺少房间 id'
            self.status_code = ERROR_DATA
            return self.render_to_response({})
        room = Room.objects.filter(room_id=rid)
        if not room.exists():
            self.message = '房间不存在'
            self.status_code = INFO_NO_EXIST
            return self.render_to_response({})
        room = room[0]
        progress = int(request.GET.get('progress', 0))
        index = int(request.GET.get('index', 0))
        reset = int(request.GET.get('reset', 0))
        if reset == 1:
            room.index = 0
            room.progress = 0
            room.save()
        if index < room.index:
            room.new = False
            return self.render_to_response(room)
        elif index > room.index:
            room.index = index
            room.progress = progress
            room.save()
            room.new = True
            return self.render_to_response(room)
        else:
            if progress < room.progress:
                room.new = False
                return self.render_to_response(room)
            room.progress = progress
            room.save()
            room.new = True
            return self.render_to_response(room)


class YoukuVideoList(CheckSecurityMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = Video
    datetime_type = 'timestamp'
    http_method_names = ['get']
    paginate_by = 40

    def get_queryset(self):
        queryset = super(YoukuVideoList, self).get_queryset().order_by('-create_time')
        video_type = int(self.request.GET.get('type', 1))
        search = self.request.GET.get('search', None)
        if search:
            return queryset.filter(video_type=2).filter(title__icontains=search)
        return queryset.filter(video_type=video_type)

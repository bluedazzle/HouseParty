# coding: utf-8
from __future__ import unicode_literals

import random
import string

import datetime

import requests
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response

# Create your views here.
from django.utils.timezone import get_current_timezone
from django.views.generic import UpdateView, DetailView, TemplateView, ListView, RedirectView, View, CreateView, \
    DeleteView
from django.views.generic.base import TemplateResponseMixin

from core.utils import upload_picture, create_game_id, create_tournament_id, create_token
from core.models import *
from myadmin.forms import AdminLoginForm
from myadmin.models import HAdmin
from core.Mixin.CheckMixin import CheckSecurityMixin, CheckAdminPermissionMixin
from core.Mixin.StatusWrapMixin import *
from core.Mixin.JsonRequestMixin import JsonRequestMixin
from core.dss.Mixin import *


class AdminLoginView(CheckSecurityMixin, AdminStatusWrapMixin, JsonRequestMixin, JsonResponseMixin, UpdateView):
    model = HAdmin
    pk_url_kwarg = 'username'
    form_class = AdminLoginForm
    http_method_names = ['post', 'options']
    include_attr = ['token', 'nick', 'phone']
    success_url = 'localhost'
    token = ''
    count = 64

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")

    def form_invalid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(AdminLoginView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json())
        return self.render_to_response(dict())

    def form_valid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(AdminLoginView, self).form_valid(form)
        if not self.object.check_password(form.cleaned_data.get('password')):
            self.message = [('password', '密码不正确')]
            self.status_code = ERROR_PASSWORD
            return self.render_to_response(dict())
        self.token = self.create_token()
        self.object.token = self.token
        self.object.save()
        self.request.session['token'] = self.token
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
            self.message = [('username', '帐号不存在')]
            self.status_code = INFO_NO_EXIST
            return None
        return obj


class AdminLogoutView(CheckSecurityMixin, CheckAdminPermissionMixin, StatusWrapMixin, JsonResponseMixin,
                      TemplateResponseMixin, View):
    http_method_names = ['get']
    template_name = 'admin/admin_login.html'

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        request.session['token'] = ''
        return self.render_to_response(dict())


class AdminIndexView(CheckSecurityMixin, CheckAdminPermissionMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    pk_url_kwarg = ''
    http_method_names = ['get']

    def get_queryset(self):
        return {
            'users': PartyUser.objects.all().count(),
            # 'chatting': ChatHistory.objects.filter(chat=True).count(),
            # 'total': ChatHistory.objects.all().count()
        }

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_queryset())


class AdminUserView(CheckSecurityMixin, CheckAdminPermissionMixin, StatusWrapMixin, JsonRequestMixin, JsonResponseMixin,
                    DetailView):
    pk_url_kwarg = 'token'
    http_method_names = ['get', 'post']
    include_attr = ['nick', 'last_login', 'phone']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        return self.render_to_response(self.admin)

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        if old_password and new_password:
            if self.admin.check_password(old_password):
                self.admin.set_password(new_password)
                self.admin.save()
                return self.render_to_response(dict())
            else:
                self.message = '原密码不正确'
                self.status_code = ERROR_PASSWORD
                return self.render_to_response(dict())
        self.message = '参数缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response(dict())


class AdminUserListView(CheckSecurityMixin, CheckAdminPermissionMixin,
                        StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    http_method_names = ['get']
    paginate_by = 50
    ordering = '-create_time'
    exclude_attr = ['token', 'password']
    model = PartyUser

    def get_queryset(self):
        queryset = super(AdminUserListView, self).get_queryset()
        query_str = self.request.GET.get('query')
        if query_str:
            queryset = queryset.filter(Q(nick__icontains=query_str) | Q(phone__icontains=query_str))
        queryset = queryset.order_by('-create_time')
        return queryset


class AdminUserForbidView(CheckSecurityMixin, CheckAdminPermissionMixin,
                          StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']
    model = PartyUser
    pk_url_kwarg = 'uid'
    count = 64

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.forbid = not self.object.forbid
        self.object.token = self.create_token()
        self.object.save()
        return self.render_to_response(dict())

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")


class AdminUserDetailView(CheckSecurityMixin, CheckAdminPermissionMixin,
                          StatusWrapMixin, JsonResponseMixin, DeleteView):
    http_method_names = ['get', 'delete']
    model = PartyUser
    pk_url_kwarg = 'uid'
    foreign = True

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.render_to_response(dict())

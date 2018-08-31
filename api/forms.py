# coding: utf-8
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password

from core.models import Verify, PartyUser

import datetime
from django.utils.timezone import get_current_timezone


class VerifyCodeForm(forms.ModelForm):
    error_messages = {
        'min_time': '请求短信时间间隔过短',
        'required': '请输入手机号',
        'phone_format': '请输入11位手机号',
        'user_exist': '该用户已注册',
    }

    code_messages = {
        'required': '请输入邀请码',
        'max_length': '请输入6位邀请码',
        'min_length': '请输入6位邀请码',
        'wrong': '邀请码不存在',
        'exist': '邀请码已使用'
    }

    phone = forms.CharField(max_length=11, error_messages=error_messages)

    # code = forms.CharField(max_length=6, min_length=6, error_messages=code_messages)

    def clean_phone(self):
        phone = unicode(self.cleaned_data.get('phone', None))
        if phone:
            # if len(phone) != 11:
            #     raise forms.ValidationError(message=self.error_messages['phone_format'], code='phone_format')
            phone_list = Verify.objects.filter(phone=phone).order_by('-create_time')
            if phone_list.exists():
                phone_obj = phone_list[0]
                now_time = datetime.datetime.now(tz=get_current_timezone())
                if now_time - phone_obj.create_time < datetime.timedelta(seconds=30):
                    raise forms.ValidationError(message=self.error_messages['min_time'], code='min_time')
            user = PartyUser.objects.filter(phone=phone)
            if user.exists():
                raise forms.ValidationError(message=self.error_messages['user_exist'], code='user_exist')
            else:
                return phone
        else:
            raise forms.ValidationError(message=self.error_messages['required'], code='required')

    # def clean_code(self):
    #     code = unicode(self.cleaned_data.get('code', None))
    #     if code:
    #         invite = Invite.objects.filter(code__iexact=code)
    #         if not invite.exists():
    #             raise forms.ValidationError(message=self.code_messages['wrong'], code='wrong')
    #         else:
    #             if invite[0].use:
    #                 raise forms.ValidationError(message=self.code_messages['exist'], code='exist')
    #     return code

    def save(self, commit=False):
        return super(VerifyCodeForm, self).save(commit)

    class Meta:
        model = Verify
        fields = ['phone']


class UserRegisterForm(forms.ModelForm):
    phone_error_messages = {
        'required': '请输入手机号',
        'unique': '帐号已存在',
        'phone_format': '请输入11位手机号',
    }

    # nick_error_messages = {
    #     'required': '请输入昵称',
    #     'unique': '昵称已存在',
    # }
    #
    # password_error_messages = {
    #     'required': '请输入密码',
    #     'min_length': '请至少输入6位以上密码',
    # }

    phone = forms.CharField(max_length=11, error_messages=phone_error_messages)
    nick = forms.CharField(max_length=20)
    # fullname = forms.CharField(max_length=100)
    # password = forms.CharField(max_length=100)

    # code = forms.CharField(max_length=6)

    # def clean_password(self):
    #     password = unicode(self.cleaned_data.get('password'))
    #     if len(password) < 6:
    #         raise forms.ValidationError(message=self.password_error_messages['min_length'], code='min_length')
    #     return password

    def clean_phone(self):
        phone = unicode(self.cleaned_data.get('phone', None))
        if len(phone) != 11:
            raise forms.ValidationError(message=self.phone_error_messages['phone_format'], code='phone_format')
        return phone

    def save(self, commit=False):
        return super(UserRegisterForm, self).save(commit)

    class Meta:
        model = PartyUser
        fields = ['phone', 'nick']


class UserResetForm(forms.ModelForm):
    password_error_messages = {
        'required': '请输入密码',
        'min_length': '请至少输入6位以上密码',
    }
    password = forms.CharField(max_length=100, error_messages=password_error_messages)
    # code = forms.CharField(max_length=6, min_length=6)
    phone = forms.CharField(max_length=11, min_length=11)

    # def clean_code(self):
    #     phone = self.cleaned_data.get('phone')
    #     code = self.cleaned_data.get('code')
    #     verify = Verify.objects.filter(phone=phone, code=code)
    #     if verify.exists():
    #         verify = verify[0]
    #         verify.delete()
    #         return code
    #     raise forms.ValidationError(message='验证码错误', code='verify_error')

    def clean_password(self):
        password = unicode(self.cleaned_data.get('password'))
        if len(password) < 6:
            raise forms.ValidationError(message=self.password_error_messages['min_length'], code='min_length')
        return password

    def save(self, commit=False):
        return super(UserResetForm, self).save(commit)

    class Meta:
        model = PartyUser
        fields = ['password', 'phone']


class UserLoginForm(forms.ModelForm):
    password_error_messages = {
        'required': '请输入密码',
        'min_length': '请至少输入6位以上密码',
    }
    password = forms.CharField(max_length=100, error_messages=password_error_messages)

    def save(self, commit=False):
        return super(UserLoginForm, self).save(commit)

    class Meta:
        model = PartyUser
        fields = []

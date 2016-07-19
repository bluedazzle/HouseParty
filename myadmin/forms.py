# coding: utf-8

from __future__ import unicode_literals
from django import forms
from DjangoUeditor.forms import UEditorField


class BaseForm(forms.Form):
    instance = None

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super(BaseForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        return self.instance


class AdminLoginForm(BaseForm):
    username_error_messages = {
        'required': '请输入帐号',
        'max_length': '请输入11位手机号',
        'min_length': '请输入11位手机号',
    }
    password_error_messages = {
        'required': '请输入密码',
    }
    username = forms.CharField(max_length=11, min_length=11, error_messages=username_error_messages)
    password = forms.CharField(max_length=50, error_messages=password_error_messages)

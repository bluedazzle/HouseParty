# coding: utf-8

from __future__ import unicode_literals

from django.utils.timezone import get_current_timezone

from core.models import PartyUser

import datetime


def check_online(*args, **kwargs):
    now_time = datetime.datetime.now(tz=get_current_timezone())
    for user in PartyUser.objects.filter(online=True):
        if now_time - user.modify_time >= datetime.timedelta(seconds=20):
            user.online = False
            user.save()

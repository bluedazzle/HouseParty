# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.hx import update_ease_user
from core.models import PartyUser

NEW_TOKEN = 'ZGBKrriEYvaXsiJjaQuhq5yntpl8ewWdxu7nRmTAhzSCkZGNket92Bf3dFbMIgLj'


class Command(BaseCommand):
    def handle(self, *args, **options):
        fail_list = []
        for itm in PartyUser.objects.all():
            if update_ease_user(itm.token, NEW_TOKEN, itm.fullname):
                print 'reset user token success'
            else:
                print 'reset user token failed'
                fail_list.append(itm.fullname)
        print 'fail list {0}'.format(fail_list)

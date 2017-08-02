# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.models import Song


class Command(BaseCommand):
    def handle(self, *args, **options):
        del_list = ['11']
        for itm in Song.objects.all():
            print itm.id
            for d in del_list:
                if d in itm.name:
                    itm.delete()
                    break

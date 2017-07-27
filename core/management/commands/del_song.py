# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.models import Song


class Command(BaseCommand):
    def handle(self, *args, **options):
        del_list = ['缺', '慢摇', '广告', '男声', '女声', '理查德', '现场版', '舞曲版', '主题曲', '铃声', '男伴奏', '女伴奏', '合作伴奏', '男同胞', '女同胞',
                    '石进', '主题曲', '降调', '混缩', '合唱', '串烧']
        for itm in Song.objects.all():
            print itm.id
            for d in del_list:
                if d in itm.name:
                    itm.delete()
                    break

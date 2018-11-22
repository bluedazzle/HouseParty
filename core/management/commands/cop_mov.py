# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.models import Video
import requests


class Command(BaseCommand):
    def handle(self, *args, **options):
        videos = Video.objects.filter(link__icontains="fibar").all()
        for video in videos:
            try:
                data = {'address': video.address, 'link': video.link, 'title': video.title,
                        'thumbnail': video.thumbnail}
                resp = requests.post('http://movie.fibar.cn/api/v1/videos/', data=data)
                print resp.content
            except Exception as e:
                print e


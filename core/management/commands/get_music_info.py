# coding: utf-8
from __future__ import unicode_literals

from mutagen.mp3 import MP3
import cStringIO
import urllib
from django.core.management.base import BaseCommand
from django_bulk_update.helper import bulk_update
from django.core.paginator import Paginator
from core.models import Song


class Command(BaseCommand):
    def handle(self, *args, **options):
        paginator = Paginator(Song.objects.all(), 1000)  # chunks of 1000, you can
        # change this to desired chunk size

        for page in range(1, paginator.num_pages + 1):
            object_list = paginator.page(page).object_list
            for row in object_list:
                try:
                    audio = MP3(cStringIO.StringIO(
                        urllib.urlopen(row.link).read()))
                    seconds = int(audio.info.length)
                    row.duration = seconds
                except Exception as e:
                    print 'ERROR IN GET MUSIC {0} INFO, REASON {1} '.format(row.link, e)
            bulk_update(object_list)
            print 'PROCESSING {0}/{1} {2}%'.format(page, paginator.num_pages, page / paginator.num_pages * 100)
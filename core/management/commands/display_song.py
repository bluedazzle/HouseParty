# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.models import Song


class Command(BaseCommand):
    def handle(self, *args, **options):
        songs = Song.objects.filter(song_type=2)
        length = len(songs)
        for i, itm in enumerate(songs):
            print '{0}/{1}'.format(i, length)
            itm.hidden = False
            itm.save()

        songs = Song.objects.filter(original='')
        length = len(songs)

        for i, itm in enumerate(songs):
            print '{0}/{1}'.format(i, length)
            itm.hidden = True
            itm.save()

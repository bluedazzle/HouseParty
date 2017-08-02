# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.models import Song


class Command(BaseCommand):
    def handle(self, *args, **options):
        exist = True
        while exist:
            songs = Song.objects.filter(dup=False).all()
            exist = songs.exists()
            if exist:
                itm = songs[0]
                print 'current id {0}: {1}'.format(itm.id, itm.name)
                dups = Song.objects.exclude(id=itm.id).filter(name=itm.name, author=itm.author)
                if dups.exists():
                    for dup in dups:
                        dup.delete()
                itm.dup = True
                itm.save()
        print 'finish'

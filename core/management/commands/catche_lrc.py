# coding: utf-8
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from core.models import Song
from song.song.qn import search_file


class Command(BaseCommand):
    def handle(self, *args, **options):
        exist = True
        while exist:
            songs = Song.objects.filter(catch_lrc=False).all()
            exist = songs.exists()
            if exist:
                itm = songs[0]
                print 'current id {0}'.format(itm.id)
                res = search_file(itm.name.replace('伴奏', ''))
                if res:
                    itm.lrc = res
                else:
                    url = self.catch_url(itm.name.replace('伴奏', ''), itm.author)
                    if url:
                        lrc = self.catch_lrc(url)
                        if lrc:
                            itm.lrc = lrc
                itm.catch_lrc = True
                itm.save()
        print 'finish'

    def catch_url(self, name, author):
        url = 'http://www.lrcgc.com/so/?q={0}+{1}'.format(name, author)
        try:
            req = requests.get(url, timeout=5)
            print req.status_code
            soup = BeautifulSoup(req.content)
            matches = soup.find_all('span', attrs={'class': 'item'})
            if matches:
                match = matches[0]
                matches = match.find_all('a')
                if matches:
                    match = matches[0]
                    return 'http://www.lrcgc.com{0}'.format(match['href'])
        except Exception as e:
            return None

    def catch_lrc(self, url):
        try:
            req = requests.get(url, timeout=5)
            print req.status_code
            soup = BeautifulSoup(req.content)
            matches = soup.find_all('a', attrs={'id': 'J_downlrc'})
            if matches:
                match = matches[0]
                return 'http://www.lrcgc.com/{0}'.format(match['href'])
        except Exception as e:
            return None

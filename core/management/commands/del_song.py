# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.models import Song


class Command(BaseCommand):
    def handle(self, *args, **options):
        Song.objects.filter(hidden=True).delete()

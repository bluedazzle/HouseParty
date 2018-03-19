# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from core.models import PartyUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        for itm in PartyUser.objects.all():
            itm.active = True
            itm.save()
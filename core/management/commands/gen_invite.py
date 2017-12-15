# coding: utf-8
from __future__ import unicode_literals

import random
import string

from django.core.management.base import BaseCommand

from core.models import Invite


class Command(BaseCommand):
    def handle(self, *args, **options):
        def create_verify_code(count=5):
            return string.join(
                random.sample('234567890abcdefghgkmnopqrstuvwxyz', count)).replace(" ", "")

        for i in xrange(100):
            Invite(code=create_verify_code()).save()
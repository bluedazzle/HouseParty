# coding: utf-8
from __future__ import unicode_literals
from uwsgidecorators import timer


@timer(10)
def check_alive(signum):
    print 'check_alive {0}'.format(signum)

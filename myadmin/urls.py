from django.conf.urls import patterns, include, url
from myadmin.views import *

urlpatterns = patterns('',
                       url(r'^login$', AdminView.as_view()),
                       url(r'^index', AdminIndexView.as_view()),
                       url(r'^setting', AdminSettingView.as_view()),
                       url(r'^logout', AdminLogoutView.as_view()),
                       url(r'^users', AdminUserListView.as_view()),
                       )

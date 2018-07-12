from django.conf.urls import patterns, include, url
from api import api_v2

urlpatterns = patterns('',
                       url(r'^weapp/auth/$', api_v2.UserAuthView.as_view()),
                       url(r'^weapp/user/$', api_v2.UserView.as_view()),
                       url(r'^rooms/$', api_v2.RoomListView.as_view()),
                       url(r'^opentime/$', api_v2.OpenTimeView.as_view()),
                       )

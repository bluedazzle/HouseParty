from django.conf.urls import patterns, include, url
from myadmin.api_views import *

urlpatterns = patterns('',
                       url(r'^login', AdminLoginView.as_view()),
                       url(r'^logout', AdminLogoutView.as_view()),
                       url(r'^index', AdminIndexView.as_view()),
                       url(r'^admin', AdminUserView.as_view()),
                       url(r'^user/(?P<uid>(\d)+)/forbid', AdminUserForbidView.as_view()),
                       url(r'^users', AdminUserListView.as_view()),
                       )

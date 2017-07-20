from django.conf.urls import patterns, include, url
from page import views

urlpatterns = patterns('',
                       url(r'^invite', views.InviteView.as_view()),
                       url(r'^guide', views.GuideView.as_view()),
                       )

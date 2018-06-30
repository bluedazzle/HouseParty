from django.conf.urls import patterns, include, url
from page import views

urlpatterns = patterns('',
                       url(r'^invite', views.InviteView.as_view()),
                       url(r'^guide', views.GuideView.as_view()),
                       url(r'^guide_android', views.AndroidGuideView.as_view()),
                       url(r'^download', views.DownloadView.as_view()),
                       url(r'^service', views.ServiceView.as_view()),
                       )

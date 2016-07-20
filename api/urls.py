from django.conf.urls import patterns, include, url
from api import views

urlpatterns = patterns('',
                       url(r'^verify', views.VerifyCodeView.as_view()),
                       url(r'^register', views.UserRegisterView.as_view()),
                       url(r'^reset', views.UserResetView.as_view()),
                       url(r'^logout', views.UserLogoutView.as_view()),
                       url(r'^login', views.UserLoginView.as_view()),
                       url(r'^heart', views.HeartView.as_view()),
                       url(r'^friend/(?P<phone>(\d)+)', views.FriendView.as_view()),
                       url(r'^friend', views.FriendView.as_view()),
                       url(r'^requests', views.RequestListView.as_view()),
                       url(r'^match', views.FriendMatchView.as_view()),
                       url(r'^hi/(?P<phone>(\d)+)', views.HookView.as_view()),
                       url(r'^room/(?P<room>(\w)+)', views.RoomView.as_view()),
                       )

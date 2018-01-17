from django.conf.urls import patterns, include, url
from api import views

urlpatterns = patterns('',
                       url(r'^invite_code', views.InviteCodeView.as_view()),
                       url(r'^codes', views.InviteListView.as_view()),
                       url(r'^verify', views.VerifyCodeView.as_view()),
                       url(r'^register', views.UserRegisterView.as_view()),
                       url(r'^reset', views.UserResetView.as_view()),
                       url(r'^logout', views.UserLogoutView.as_view()),
                       url(r'^login', views.UserLoginView.as_view()),
                       url(r'^bind', views.BindPhoneView.as_view()),
                       url(r'^third_login', views.ThirdLoginView.as_view()),
                       url(r'^sms_login', views.SMSLoginView.as_view()),
                       url(r'^heart', views.HeartView.as_view()),
                       url(r'^friends', views.FriendListView.as_view()),
                       url(r'^friend/(?P<phone>(\d)+)', views.FriendView.as_view()),
                       url(r'^friend', views.FriendView.as_view()),
                       url(r'^requests', views.RequestListView.as_view()),
                       url(r'^invite', views.InviteView.as_view()),
                       url(r'^match', views.FriendMatchView.as_view()),
                       url(r'^mayknow', views.FriendMatchView.as_view()),
                       url(r'^hi/(?P<phone>(\d)+)', views.HookView.as_view()),
                       url(r'^exit_room/$', views.ExitView.as_view()),
                       url(r'^rooms/$', views.RoomListView.as_view()),
                       url(r'^room/(?P<room>(\w)+)/singer/create/$', views.SingerCreateView.as_view()),
                       url(r'^room/(?P<room>(\w)+)/singers/$', views.SingerListView.as_view()),
                       url(r'^room/(?P<room>(\w)+)/$', views.RoomView.as_view()),
                       url(r'^room/$', views.RoomView.as_view()),
                       url(r'^confirm/(?P<did>(\d)+)', views.DeleteVerifyView.as_view()),
                       url(r'^search', views.SearchView.as_view()),
                       url(r'^info', views.InfoView.as_view()),
                       url(r'^avatar', views.UserAvatarView.as_view()),
                       url(r'^progress_control', views.ProgressControlView.as_view()),
                       url(r'^gift', views.PresentListView.as_view()),
                       url(r'^send_gift', views.SendGiftView.as_view()),
                       url(r'^songs', views.SongListView.as_view()),
                       url(r'^user/(?P<fullname>(\d)+)', views.UserInfoView.as_view()),
                       url(r'^report', views.ReportView.as_view()),
                       url(r'^song/create', views.SongInfoCreateView.as_view()),
                       )

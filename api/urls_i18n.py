from django.conf.urls import patterns, include, url
from api import api_i18n

urlpatterns = patterns('',
                       url(r'^sms_login/$', api_i18n.SMSLoginView.as_view()),
                       url(r'^verify/$', api_i18n.VerifyCodeView.as_view()),
                       url(r'^get_firebase/$', api_i18n.GetFirebaseView.as_view()),
                       url(r'^room_invite/$', api_i18n.RoomInviteView.as_view()),
                       )

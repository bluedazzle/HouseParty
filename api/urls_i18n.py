from django.conf.urls import patterns, include, url
from api import api_i18n

urlpatterns = patterns('',
                       url(r'^sms_login/$', api_i18n.SMSLoginView.as_view()),
                       url(r'^verify/$', api_i18n.VerifyCodeView.as_view()),
                       )

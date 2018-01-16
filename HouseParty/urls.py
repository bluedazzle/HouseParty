from django.conf.urls import patterns, include, url
from django.contrib import admin
from api.views import RedirectView
from HouseParty import settings

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'HouseParty.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^test/socket/', include('django_socketio.urls')),
                       url(r'^api/v1/', include('api.urls')),
                       url(r'^page/', include('page.urls')),
                       url(r'^admin/api/', include('myadmin.api_urls')),
                       url(r'^admin/', include('myadmin.urls')),
                       url(r'^download/', RedirectView.as_view()),
                       url(r'^site_admin/', include(admin.site.urls)),
                       url(r'^s/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_MEDIA}),
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_MEDIA}),
                       )

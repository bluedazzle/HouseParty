from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView, TemplateView

from core.models import PartyUser, Room, Secret


class InviteView(DetailView):
    template_name = 'invite.html'
    http_method_names = ['get']
    model = PartyUser

    def get_object(self, queryset=None):
        phone = self.request.GET.get('fullname')
        if phone:
            users = PartyUser.objects.filter(fullname=phone)
            if users.exists():
                return users[0]
        return None

    def get_context_data(self, **kwargs):
        context = super(InviteView, self).get_context_data(**kwargs)
        room_id = self.request.GET.get('room')
        room = Room.objects.filter(room_id=room_id)
        secret = Secret.objects.all()[0]
        if room.exists():
            room = room[0]
            context['room'] = room
            context['version'] = secret.version
        return context


class GuideView(DetailView):
    template_name = 'guide.html'
    http_method_names = ['get']

    def get_object(self, queryset=None):
        phone = self.request.GET.get('room')
        if phone:
            users = Room.objects.filter(room_id=phone)
            if users.exists():
                return users[0]
        return None

    def get_context_data(self, **kwargs):
        context = super(GuideView, self).get_context_data(**kwargs)
        secret = Secret.objects.all()[0]
        context['version'] = secret.version
        return context


class AndroidGuideView(DetailView):
    template_name = 'guide_android.html'
    http_method_names = ['get']

    def get_object(self, queryset=None):
        phone = self.request.GET.get('room')
        if phone:
            users = Room.objects.filter(room_id=phone)
            if users.exists():
                return users[0]
        return None

    def get_context_data(self, **kwargs):
        context = super(AndroidGuideView, self).get_context_data(**kwargs)
        secret = Secret.objects.all()[0]
        context['version'] = secret.version
        return context


class DownloadView(DetailView):
    template_name = 'download.html'
    http_method_names = ['get']

    def get_object(self, queryset=None):
        return None

    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)
        secret = Secret.objects.all()[0]
        context['version'] = secret.version
        return context


class ServiceView(TemplateView):
    template_name = 'service.html'
    http_method_names = ['get']

from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView

from core.models import PartyUser


class InviteView(DetailView):
    template_name = 'invite.html'
    http_method_names = ['get']
    model = PartyUser

    def get_object(self, queryset=None):
        phone = self.request.GET.get('phone')
        if phone:
            users = PartyUser.objects.filter(phone=phone)
            if users.exists():
                return users[0]
        return None

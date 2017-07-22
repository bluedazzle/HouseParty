from django.contrib import admin
from core.models import *


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    search_fields = ['fullname', ]


admin.site.register(PartyUser, UserAdmin)
admin.site.register(Secret)
admin.site.register(Verify)
# admin.site.register(FriendRequest)
# admin.site.register(FriendNotify)
# admin.site.register(Hook)
admin.site.register(Room)
# admin.site.register(DeleteNotify)
admin.site.register(Song)

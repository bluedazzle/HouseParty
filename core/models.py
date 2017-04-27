# coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


# Create your models here.

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Room(BaseModel):
    room_id = models.CharField(max_length=64, unique=True)
    progress = models.IntegerField(default=0)
    index = models.IntegerField(default=0)

    # participants = models.ManyToManyField(PartyUser, related_name='my_all_rooms', blank=True)

    def number(self):
        return self.room_participants.all().count()

    def destroy(self):
        if self.number() == 0:
            self.delete()

    def search(self, user):
        return True if user in self.room_participants.all() else False

    def __unicode__(self):
        return self.room_id


class PartyUser(BaseModel, AbstractBaseUser):
    nick = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=11, unique=True)
    fullname = models.CharField(max_length=64, default='')
    avatar = models.CharField(max_length=256, default='/s/image/avatar.png', null=True, blank=True)
    friend_list = models.ManyToManyField('self', related_name='friend_by', blank=True)
    online = models.BooleanField(default=False)
    forbid = models.BooleanField(default=False)
    room = models.ForeignKey(Room, related_name='room_participants', null=True, blank=True, on_delete=models.SET_NULL)
    token = models.CharField(max_length=64, unique=True)

    USERNAME_FIELD = 'phone'

    def chat(self):
        return True if self.room else False

    def __unicode__(self):
        return '{0}-{1}'.format(self.nick, self.phone)


class Verify(BaseModel):
    code = models.CharField(max_length=10)
    phone = models.CharField(max_length=13)

    def __unicode__(self):
        return self.phone


class Secret(BaseModel):
    secret = models.CharField(max_length=64)
    info = models.CharField(max_length=20, default='system')

    def __unicode__(self):
        return self.info


class FriendRequest(BaseModel):
    requester = models.ForeignKey(PartyUser, related_name='my_requests')
    add = models.ForeignKey(PartyUser, related_name='request_list')

    def __unicode__(self):
        return '{0}-{1}'.format(self.requester.nick, self.add.nick)


class FriendNotify(BaseModel):
    friend = models.ForeignKey(PartyUser, related_name='rel_friends_notify')
    belong = models.ForeignKey(PartyUser, related_name='friend_notifies')
    message = models.CharField(max_length=100, default='')

    def __unicode__(self):
        return '{0} | 属于{1}的好友列表'.format(self.friend.nick, self.belong.nick)


class Hook(BaseModel):
    author = models.ForeignKey(PartyUser, related_name='my_hooks')
    hook_to = models.ForeignKey(PartyUser, related_name='hooked_by_others')

    def __unicode__(self):
        return "{0}->{1}".format(self.author.nick, self.hook_to.nick)


class DeleteNotify(BaseModel):
    belong = models.ForeignKey(PartyUser, related_name='deleted_by')
    deleter = models.ForeignKey(PartyUser, related_name='delete_list')

    def __unicode__(self):
        return '{0} delete {1}'.format(self.deleter.nick, self.belong.nick)

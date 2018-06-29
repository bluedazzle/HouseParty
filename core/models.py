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
    name = models.CharField(max_length=100, default='')
    progress = models.IntegerField(default=0)
    index = models.IntegerField(default=0)
    creator_id = models.IntegerField(default=0)
    creator_nick = models.CharField(default='', max_length=100)
    cover = models.CharField(max_length=256, default='')
    priority = models.IntegerField(default=0)
    is_micro = models.BooleanField(default=False)
    ding = models.BooleanField(default=False)

    # participants = models.ManyToManyField(PartyUser, related_name='my_all_rooms', blank=True)

    def number(self):
        return self.room_participants.all().count()

    def destroy(self):
        if self.number() == 0:
            self.delete()

    def search(self, user):
        return True if user in self.room_participants.all() else False

    def __unicode__(self):
        return '{0}-{1}'.format(self.room_id, self.name)


class PartyUser(BaseModel, AbstractBaseUser):
    sex_choices = (
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    )

    nick = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=11, default='', null=True, blank=True)
    fullname = models.CharField(max_length=64, unique=True)
    avatar = models.CharField(max_length=256, null=True, blank=True, default='http://ktv.fibar.cn/static/image/avatar.png')
    friend_list = models.ManyToManyField('self', related_name='friend_by', blank=True)
    online = models.BooleanField(default=False)
    forbid = models.BooleanField(default=False)
    sex = models.IntegerField(default=0, choices=sex_choices)
    headline = models.CharField(max_length=512, default='', null=True, blank=True)
    room = models.ForeignKey(Room, related_name='room_participants', null=True, blank=True, on_delete=models.SET_NULL)
    qq_open_id = models.CharField(max_length=128, default='', blank=True, null=True)
    wx_open_id = models.CharField(max_length=128, default='', blank=True, null=True)
    token = models.CharField(max_length=64, unique=True)
    active = models.BooleanField(default=True)

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
    version = models.CharField(max_length=20, default='1.0.3')
    num = models.IntegerField(default=324823)

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


# class Video(BaseModel):
#     type_choices = (
#         (1, '优酷'),
#         (2, '自建'),
#         (3, '电视直播'),
#     )
#     address = models.CharField(max_length=512, default='')
#     title = models.CharField(max_length=100, default='', null=True, blank=True)
#     thumbnail = models.CharField(max_length=1024, default='', null=True, blank=True)
#     link = models.CharField(max_length=1024, default='', null=True, blank=True)
#     view_count = models.IntegerField(default=0)
#     yid = models.CharField(max_length=100, default='', null=True, blank=True)
#     duration = models.FloatField(default=0)
#     video_type = models.IntegerField(default=1, choices=type_choices)
#     hidden = models.BooleanField(default=False)
#
#     def __unicode__(self):
#         return self.title
#
#     def save(self, force_insert=False, force_update=False, using=None,
#              update_fields=None):
#         import re
#         from youku import YoukuVideos
#         if self.video_type == 1:
#             video_id = re.findall(r'id_(.*)==.html', self.address)[0]
#             youku = YoukuVideos('d124ea671a7616d5')
#             video = youku.find_video_by_id(video_id)
#             self.title = video.get('title')
#             self.yid = video_id
#             self.thumbnail = video.get('thumbnail', '')
#             self.link = video.get('link', '')
#             self.duration = video.get('duration', 0)
#             self.view_count = video.get('view_count', 0)
#         elif self.video_type == 2:
#             self.link = self.address
#             self.thumbnail = '{0}?vframe/jpg/offset/0/w/200/h/112/'.format(self.address)
#         else:
#             self.link = self.address
#         return super(Video, self).save(force_insert, force_update, using, update_fields)


class Song(BaseModel):
    song_choice = (
        (1, '爬虫'),
        (2, '全民')
    )
    name = models.CharField(max_length=150, default='')
    author = models.CharField(max_length=150, default='')
    link = models.CharField(max_length=256)
    lrc = models.CharField(max_length=256, default='')
    hidden = models.BooleanField(default=False)
    dup = models.BooleanField(default=False)
    catch_lrc = models.BooleanField(default=False)
    recommand = models.IntegerField(default=0)
    original = models.CharField(default='', max_length=150, null=True, blank=True)
    hash = models.CharField(default='', max_length=128, blank=True, null=True)
    song_type = models.IntegerField(default=1, choices=song_choice)
    duration = models.IntegerField(default=0)

    def __unicode__(self):
        return '{0}-{1}'.format(self.name, self.author)


class Present(BaseModel):
    receiver = models.ForeignKey(PartyUser, related_name='gifts', null=True)
    belong = models.ForeignKey(PartyUser, related_name='send_gifts')
    name = models.CharField(default='鲜花', max_length=20)

    def __unicode__(self):
        return self.name


class Report(BaseModel):
    content = models.TextField(default='')
    reporter = models.ForeignKey(PartyUser, related_name='user_reports')
    reported = models.ForeignKey(PartyUser, related_name='user_reported')

    def __unicode__(self):
        return self.content


class Singer(BaseModel):
    song = models.ForeignKey(Song, related_name='song_singers')
    creator = models.ForeignKey(PartyUser, related_name='song_users')
    room = models.ForeignKey(Room, related_name='song_rooms')

    def __unicode__(self):
        return '{0}: {1}'.format(self.room.name, self.creator.nick)


class Invite(BaseModel):
    code = models.CharField(max_length=6, unique=True)
    use = models.BooleanField(default=False)
    bind = models.ForeignKey(PartyUser, related_name='user_invite', null=True, blank=True)

    def __unicode__(self):
        return self.code

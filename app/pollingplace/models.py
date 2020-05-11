from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import secrets
from mongoengine import *


class Categories(models.Model):
    cid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'

class PollOptions(models.Model):
    oid = models.AutoField(primary_key=True)
    pid = models.ForeignKey('Polls', on_delete=models.CASCADE)
    optiontext = models.TextField(blank=False, null=False) 

    def __str__(self):
        return self.optiontext

    class Meta:
        db_table = 'poll_options'


class PollResponses(models.Model):
    uid = models.ForeignKey('Users', on_delete=models.CASCADE)
    pid = models.ForeignKey('Polls', on_delete=models.CASCADE)
    oid = models.ForeignKey('PollOptions', on_delete=models.CASCADE)

    class Meta:
        db_table = 'poll_responses'
        unique_together = (('uid', 'pid'),)


class Polls(models.Model):
    pid = models.AutoField(primary_key=True, db_index=True)
    uid = models.ForeignKey('Users', on_delete=models.CASCADE)
    creation_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)
    topic = models.TextField(blank=False, null=False)
    url = models.CharField(max_length=50, blank=True, null=True) 
    active = models.BooleanField(blank=False, null=False)
    public = models.BooleanField(blank=False, null=False)
    flag = models.IntegerField(blank=False, null=False)
    cid = models.ForeignKey('Categories', on_delete=models.CASCADE)
    state = models.CharField(max_length=50, blank=True, null=True)
    zipcode = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return  str(self.pid)

    def get_absolute_url(self):
        return reverse( 'vote', args=[self.pk])

    class Meta:
        db_table = 'polls'


class Users(models.Model):
    uid =  models.AutoField(primary_key=True)
    username = models.CharField(max_length=100,  blank=False, null=False) 
    password = models.CharField(max_length=100,  blank=False, null=False)
    givenname = models.CharField(max_length=100,  blank=False, null=False)  
    familyname = models.CharField(max_length=100,  blank=False, null=False) 
    email = models.CharField(max_length=100, blank=False, null=False) 
    address = models.CharField(max_length=100,  blank=False, null=False) 
    city = models.CharField(max_length=100, blank=True, null=True)  
    state = models.CharField(max_length=100, blank=True, null=True)  
    zipcode = models.CharField(max_length=100,  blank=False, null=False)  
    imageurl = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'

class Music(Document):
    AlbumID_Rank = StringField(required=True)
    Artist = StringField(max_length=500)
    Album = StringField(max_length=500)
    Release_Year = StringField(max_length=500)
    Spotify_Album  = StringField(max_length=500)
    Description = StringField(max_length=500)
    wiki = StringField(max_length=500)
    Duration = StringField(max_length=500)
    Minutes = StringField(max_length=500)
    Seconds = StringField(max_length=500)
    Total_Seconds = StringField(max_length=500)
    Label = StringField(max_length=500)
    Sub_Metal_Genre = StringField(max_length=500)
    Rating = StringField(max_length=500)
    Rolling_Stone_Rating = StringField(max_length=500)

class PollViewModel(models.Model):
    pid = models.IntegerField(primary_key=True)
    topic = models.TextField()
    name = models.TextField()
    num_votes = models.IntegerField()
    time_remaining = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'polls_view'



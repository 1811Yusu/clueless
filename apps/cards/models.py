from typing import Tuple
from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import SET, SET_NULL, CASCADE
from apps.user.models import User
from django.db.models.fields import TextField
from django.db.models.fields.related import ForeignKey
from core import settings
from core.settings import AUTH_PASSWORD_VALIDATORS, AUTH_USER_MODEL

# Create your models here.


class Pin(models.Model):
    image = models.ImageField(upload_to="pins/%y/%m/%d", null=True, blank=True)
    video = models.FileField(upload_to="video/%y/%m/%d", null=True, blank=True)
    title = models.CharField(max_length=50)
    description = models.CharField("Description", max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    creator = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    seen_by = models.ManyToManyField(AUTH_USER_MODEL, through="History", related_name="seen_pins")

    def __str__(self):
        return self.title
    


class Board(models.Model):
    name = models.CharField(max_length=50)
    visibility = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.PROTECT)
    pins = models.ManyToManyField('Pin', related_name="boards",blank=True)

    def __str__(self):
        return self.name
    


class Save(models.Model):
    pin = models.ForeignKey('Pin', on_delete=models.CASCADE )
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    saved_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'pin'),)
        ordering=['-saved_at']

class Comment(models.Model):
    user = models.ForeignKey(User, 
                             on_delete=models.CASCADE, 
                             related_name='comments')
    pin = models.ForeignKey(Pin, on_delete=SET_NULL, null=True)
    creator = models.ForeignKey(AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'Комментарий от {self.user.username}'

class Reply(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=SET_NULL, null=True)
                            
    comment = models.ForeignKey(Comment, on_delete=CASCADE, null=True)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, related_name="sent_messages")
    content = models.TextField()

    time = models.DateTimeField()


class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'pin'),)
        ordering = ['-time']


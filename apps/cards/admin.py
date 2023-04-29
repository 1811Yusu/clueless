from django.contrib import admin
from .models import Board, History, Pin, Comment, Reply, Save


admin.site.register(Pin)
admin.site.register(Board)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Save)
admin.site.register(History)

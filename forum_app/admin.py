from django.contrib import admin
from .models import *


@admin.register(Post)
class PostAdminPanel(admin.ModelAdmin):
    list_display_links = ['title']
    list_display = ['id', 'title', 'author']


@admin.register(Comment)
class CommentAdminPanel(admin.ModelAdmin):
    list_display = ['id', 'text', 'author']

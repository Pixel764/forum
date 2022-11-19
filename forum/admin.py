from django.contrib import admin
from .models import *


@admin.register(Post)
class PostAdminPanel(admin.ModelAdmin):
    list_display_links = ['title']
    list_display = ['id', 'title', 'author', 'published_date']
    filter_horizontal = ['likes']
    raw_id_fields = ['author']
    search_fields = ['id']
    search_help_text = 'Search by id'
    sortable_by = ['published_date']

    def save_model(self, request, obj, form, change):
        if not request.POST['author']:
            obj.author = request.user
        return super(PostAdminPanel, self).save_model(request, obj, form, change)

    def delete_queryset(self, request, queryset):
        for i in queryset:
            i.delete()


@admin.register(Comment)
class CommentAdminPanel(admin.ModelAdmin):
    list_display = ['id', 'get_post_id', 'author']
    list_select_related = ['post', 'author']
    raw_id_fields = ['post', 'author']

    def save_model(self, request, obj, form, change):
        if not request.POST['author']:
            obj.author = request.user
        return super(CommentAdminPanel, self).save_model(request, obj, form, change)

    @admin.display(description='Post id')
    def get_post_id(self, obj):
        return obj.post.id

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .forms import SignUpForm, AdminPanelEditProfileForm
from users.models import CustomUserModel, EmailCode


@admin.register(CustomUserModel)
class CustomUserAdmin(UserAdmin):
    add_form = SignUpForm
    form = AdminPanelEditProfileForm
    list_display = ['username', 'email', 'email_confirmed']
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'get_profile_image', 'email_confirmed')
        }),
        ('Personal info', {
            'fields': ('email',)
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    readonly_fields = ['get_profile_image']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'captcha'),
        }),
    )

    @admin.display(description='Profile image')
    def get_profile_image(self, obj):
        return mark_safe(f'<img height=80 width=80 src={obj.profile_image.url}>')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(EmailCode)
class EmailCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'code']

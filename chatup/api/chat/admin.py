from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class ImageUsersInline(admin.TabularInline):
    model = models.Image.custom_owners.through


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = 'type', 'description'
    inlines = ImageUsersInline,


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = 'sid',
    readonly_fields = 'sid', 'name', 'name_ru'


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    search_fields = 'username',
    list_display = 'username', 'email', 'role'


CustomUserAdmin.fieldsets += (_('Additional fields'), {
    'fields': ('watchtime', 'username_color', 'role', 'role_icon')
}),


@admin.register(models.Broadcast)
class BroadCastAdmin(admin.ModelAdmin):
    list_display = 'title', 'id', 'streamer'
    readonly_fields = 'id', 'created', 'updated'
    search_fields = 'title', 'source_link'


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = 'text', 'id', 'author', 'broadcast'
    readonly_fields = 'id', 'created', 'updated'
    search_fields = 'text',

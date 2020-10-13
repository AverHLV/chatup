from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = 'sid',
    readonly_fields = 'sid', 'name', 'name_ru'


@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    search_fields = 'username',
    list_display = 'username', 'email', 'role'


CustomUserAdmin.fieldsets += (_('Additional fields'), {
    'fields': ('watchtime', 'username_color', 'role')
}),


@admin.register(models.Broadcast)
class BroadCastAdmin(admin.ModelAdmin):
    list_display = 'streamer', 'title'
    search_fields = 'title', 'source_link'

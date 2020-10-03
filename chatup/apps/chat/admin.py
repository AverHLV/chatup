from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = 'sid',
    readonly_fields = 'sid', 'name', 'name_ru'


@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    search_fields = 'username', 'role'
    list_display = 'username', 'email', 'role'


CustomUserAdmin.fieldsets += ('Additional fields', {
    'fields': ('watched_time', 'nick_color', 'role')
}),

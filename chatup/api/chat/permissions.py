from rest_framework import permissions
from .models import Role


class IsAdminStreamerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role.sid in {Role.SIDS.ADMIN, Role.SIDS.STREAMER}


class IsStreamer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role.sid == Role.SIDS.STREAMER


class IsStreamerOrReadOnly(IsStreamer):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.id == obj.streamer_id

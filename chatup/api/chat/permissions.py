from rest_framework import permissions
from .models import Role


class IsBroadcastStreamer(permissions.BasePermission):
    """ Allow unsafe requests only for superusers or broadcast streamers """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role.sid == Role.SIDS.streamer \
            if request.method not in permissions.SAFE_METHODS else True

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.id == obj.streamer_id \
            if request.method not in permissions.SAFE_METHODS else True

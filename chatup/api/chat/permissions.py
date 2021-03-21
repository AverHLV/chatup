from rest_framework import permissions
from .models import Role


class IsStreamer(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_permission(request, view) and \
            (request.user.is_superuser or request.user.role.sid == Role.SIDS.STREAMER)


class IsBroadcastStreamer(IsStreamer):
    """ Allow unsafe requests only for superusers or broadcast streamers """

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.id == obj.streamer_id \
            if request.method not in permissions.SAFE_METHODS else True

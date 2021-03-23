from rest_framework import permissions
from .models import Role


class IsStreamer(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role.sid == Role.SIDS.STREAMER


class IsSafeOrStreamer(IsStreamer):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_permission(request, view)


class IsBroadcastStreamer(IsStreamer):
    """ Allow unsafe requests only for superusers or broadcast streamers """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.id == obj.streamer_id

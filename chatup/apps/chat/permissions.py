from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from .models import STREAMER_ROLE_SID


class IsBroadcastStreamer(permissions.BasePermission):
    """ Allow unsafe requests only for superusers or broadcast streamers """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role.sid == STREAMER_ROLE_SID \
            if request.method not in SAFE_METHODS else True

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.id == obj.streamer_id \
            if request.method not in SAFE_METHODS else True

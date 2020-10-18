from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from .models import STREAMER_ROLE_SID


class IsAuthenticatedOrGET(permissions.IsAuthenticated):
    """ Allow GET requests for unauthorized users """

    def has_permission(self, request, view):
        return True if request.method == 'GET' else super().has_permission(request, view)


class IsBroadcastStreamer(permissions.BasePermission):
    """ Allow unsafe requests only for superusers or broadcast streamers """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role.sid == STREAMER_ROLE_SID \
            if request.method not in SAFE_METHODS else True

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.id == obj.streamer_id \
            if request.method not in SAFE_METHODS else True


class IsBroadcastInactive(permissions.BasePermission):
    """ Only inactive broadcasts can be deleted """

    def has_object_permission(self, request, view, obj):
        return not obj.is_active if request.method == 'DELETE' else True

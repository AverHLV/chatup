from rest_framework.views import Response
from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """ Limit-offset pagination without next/previous fields """

    def get_paginated_response(self, data):
        return Response({
            'total_count': self.count,
            'result': data,
        })

from rest_framework import viewsets
from rest_framework.response import Response


class ModelViewSetBase(viewsets.ModelViewSet):
    """ Custom viewset with a couple of helpers """

    serializer_action_classes: dict = {}
    filterset_action_fields: dict = {}

    def get_serializer_class(self):
        """ Look for serializer class in actions dictionary first """

        return self.serializer_action_classes.get(self.action) or super().get_serializer_class()

    def get_filters(self, request) -> dict:
        """ Build filters for custom actions """

        filters = {}

        for field in self.filterset_action_fields[self.action]:
            value = request.query_params.get(field, None)
            if value is not None:
                filters[field] = value

        return filters

    def list_response(self, queryset):
        """ List action for custom queryset """

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

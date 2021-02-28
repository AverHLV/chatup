from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import get_language_from_request

from rest_framework import serializers


class TranslatedModelSerializer(serializers.ModelSerializer):
    """
    Model serializer that changes field source depending on the request language.

    Cannot be used as a nested serializer. Mapping will be skipped without a request
    context. Localized fields (<field_name>_<language_code>) should be omitted
    in the serializer meta
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context is None:
            return

        lang = get_language_from_request(self.context['request'])

        if lang != settings.LANGUAGES[0][0]:
            for field_name in self.translated_fields:
                self.fields[field_name].source_attrs = [f'{field_name}_{lang}']

    @cached_property
    def translated_fields(self) -> list:
        """ Get a list of field names with a complete translation """

        field_names = {field.name for field in self.Meta.model._meta.fields}

        return [
            field_name
            for field_name in self.fields
            if all(f'{field_name}_{lang[0]}' in field_names for lang in settings.LANGUAGES[1:])
        ]

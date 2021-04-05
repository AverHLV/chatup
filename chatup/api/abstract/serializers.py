import base64

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import get_language_from_request, gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from PIL import Image, ImageSequence
from io import BytesIO


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


class BinaryImageField(serializers.Field):
    """ b64 images to binary data converter """

    custom_error_messages = {
        'invalid_image': _(
            'Upload a valid image. The file you uploaded was either not an image or a corrupted image.'
        ),
    }

    def __init__(self, *args, size=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = size

    def to_representation(self, value):
        return base64.b64encode(value)

    def to_internal_value(self, data):
        try:
            decoded_image = base64.b64decode(data)
        except base64.binascii.Error:
            raise ValidationError(self.custom_error_messages['invalid_image'])

        image_buffer = BytesIO(decoded_image)

        try:
            Image.open(image_buffer).verify()
        except Exception:
            raise ValidationError(self.custom_error_messages['invalid_image'])

        if self.size:
            image_buffer = self.resize_image(image_buffer)
        return image_buffer.getvalue()

    def resize_image(self, file: BytesIO) -> BytesIO:
        """ Resize image depending on its extension """

        image = Image.open(file)
        ext = image.format
        resized_image_buffer = BytesIO()

        def _thumbnails(_frames, _size):
            for frame in _frames:
                thumbnail = frame.copy()
                thumbnail.thumbnail(_size, Image.ANTIALIAS)
                yield thumbnail

        if 'GIF' == ext:
            frames = ImageSequence.Iterator(image)
            frames = _thumbnails(frames, self.size)
            image = next(frames)
            image.save(resized_image_buffer, format=ext, save_all=True, append_images=list(frames), loop=0)
        else:
            image = image.resize(self.size)
            image.save(resized_image_buffer, format=ext)

        return resized_image_buffer

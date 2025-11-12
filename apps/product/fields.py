import base64
import binascii
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class FlexibleImageField(serializers.ImageField):
    """
    Accepts both uploaded files and base64-encoded data URLs.
    """

    def to_internal_value(self, data):
        if isinstance(data, str):
            if ";base64," in data:
                header, encoded = data.split(";base64,", 1)
                file_ext = header.split("/")[-1] if "/" in header else "png"
                try:
                    decoded = base64.b64decode(encoded)
                except binascii.Error as exc:
                    raise serializers.ValidationError("Rasm ma'lumotini o'qib bo'lmadi.") from exc
                data = ContentFile(decoded, name=f"{uuid.uuid4().hex}.{file_ext}")
        return super().to_internal_value(data)


class MultipleImageUploadField(serializers.ListField):
    """
    Normalizes single or multiple uploads into a list of FlexibleImageField items.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("child", FlexibleImageField())
        kwargs.setdefault("allow_empty", True)
        kwargs.setdefault("required", False)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if data in (None, "", []):
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return super().to_internal_value(data)

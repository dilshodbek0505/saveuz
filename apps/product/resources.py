import base64
import binascii
import os
import uuid
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from import_export import fields, resources
from import_export.widgets import Widget
from PIL import Image

from apps.main.models import Category, Market, Product

ALLOWED_IMPORT_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_IMPORT_MIME_TYPES = {"image/jpeg", "image/png", "image/jpg"}


class TranslatedForeignKeyWidget(Widget):
    def __init__(self, model, field="name"):
        super().__init__()
        self.model = model
        self.field = field
        self.language_codes = [code for code, _ in settings.LANGUAGES]

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None

        value = value.strip()
        lookup = Q(**{f"{self.field}__iexact": value})
        for lang_code in self.language_codes:
            lookup |= Q(**{f"{self.field}_{lang_code}__iexact": value})

        try:
            return self.model.objects.get(lookup)
        except self.model.DoesNotExist as exc:
            raise ValueError(
                _("%(model)s with name '%(value)s' not found.")
                % {"model": self.model.__name__, "value": value}
            ) from exc
        except self.model.MultipleObjectsReturned as exc:
            raise ValueError(
                _("Multiple %(model)s entries found for '%(value)s'.")
                % {"model": self.model.__name__, "value": value}
            ) from exc

    def render(self, value, obj=None, **kwargs):
        if not value:
            return ""
        return value.name


class ImageFieldWidget(Widget):
    TARGET_SIZE = (256, 256)

    def __init__(self, max_size_mb=2):
        super().__init__()
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def _load_from_path(self, value):
        file_path = value.strip()
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if not os.path.isfile(file_path):
            raise ValueError(_("Image '%(value)s' not found.") % {"value": value})

        extension = os.path.splitext(file_path)[1].lower()
        if extension not in ALLOWED_IMPORT_EXTENSIONS:
            raise ValueError(
                _("Only JPG and PNG images are supported for import (got '%(ext)s').")
                % {"ext": extension or _("unknown")}
            )

        if os.path.getsize(file_path) > self.max_size_bytes:
            raise ValueError(
                _("Image '%(value)s' exceeds the %(limit)s MB limit.")
                % {"value": value, "limit": self.max_size_mb}
            )

        filename = os.path.basename(file_path)
        with open(file_path, "rb") as image_file:
            file_content = image_file.read()

        with Image.open(BytesIO(file_content)) as image:
            image = self._resize_image(image)
            return self._image_to_content_file(image, filename)

    def _load_from_base64(self, data):
        header, encoded = data.split(";base64,", 1)
        mime_type = header.split(":")[-1] if ":" in header else header
        mime_type = mime_type.strip().lower()
        if mime_type not in ALLOWED_IMPORT_MIME_TYPES:
            raise ValueError(_("Only JPG and PNG images can be imported."))

        try:
            raw = base64.b64decode(encoded)
        except binascii.Error as exc:
            raise ValueError(_("Image data is not valid base64.")) from exc

        if len(raw) > self.max_size_bytes:
            raise ValueError(
                _("Provided image exceeds the %(limit)s MB limit.")
                % {"limit": self.max_size_mb}
            )

        extension = "jpg" if mime_type in {"image/jpeg", "image/jpg"} else "png"
        filename = f"{uuid.uuid4().hex}.{extension}"

        with Image.open(BytesIO(raw)) as image:
            image = self._resize_image(image)
            return self._image_to_content_file(image, filename)

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None

        value = value.strip()
        if ";base64," in value:
            return self._load_from_base64(value)

        return self._load_from_path(value)

    def render(self, value, obj=None, **kwargs):
        if not value:
            return ""
        return value.name

    def _resize_image(self, image):
        if image.size == self.TARGET_SIZE:
            return image

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA") if image.mode in ("P", "LA") else image.convert("RGB")

        return image.resize(self.TARGET_SIZE, Image.LANCZOS)

    def _image_to_content_file(self, image, filename):
        extension = os.path.splitext(filename)[1].lower()
        format_ = "JPEG" if extension in {".jpg", ".jpeg"} else "PNG"

        buffer = BytesIO()
        if format_ == "JPEG" and image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(buffer, format=format_, optimize=True)
        buffer.seek(0)
        return ContentFile(buffer.read(), name=filename)


class ProductResource(resources.ModelResource):
    IMAGE_MAX_SIZE_MB = 2

    id = fields.Field(column_name="id", attribute="id", readonly=True)
    name = fields.Field(column_name="name", attribute="name")
    price = fields.Field(column_name="price", attribute="price")
    image = fields.Field(
        column_name="image",
        attribute="image",
        widget=ImageFieldWidget(max_size_mb=IMAGE_MAX_SIZE_MB),
    )
    discount_price = fields.Field(
        column_name="discount_price", attribute="discount_price", readonly=True
    )
    discount_type = fields.Field(
        column_name="discount_type", attribute="discount_type", readonly=True
    )
    discount_value = fields.Field(
        column_name="discount_value", attribute="discount_value", readonly=True
    )
    category = fields.Field(
        column_name="category",
        attribute="category",
        widget=TranslatedForeignKeyWidget(Category, "name"),
    )
    market = fields.Field(
        column_name="market",
        attribute="market",
        widget=TranslatedForeignKeyWidget(Market, "name"),
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "image",
            "discount_price",
            "discount_type",
            "discount_value",
            "category",
            "market",
        )
        export_order = (
            "id",
            "name",
            "price",
            "image",
            "discount_price",
            "discount_type",
            "discount_value",
            "category",
            "market",
        )

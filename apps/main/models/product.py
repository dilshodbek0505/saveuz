from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image

from apps.main.models import BaseModel, Market

# Image validation constants
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
MAX_IMAGE_WIDTH = 1080
MAX_IMAGE_HEIGHT = 1920


def validate_image_size(image):
    """
    Validates that the image file size does not exceed the maximum allowed size.
    """
    if image.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            _("Image file size exceeds %(max_size)s MB. Current size: %(current_size).2f MB.")
            % {
                "max_size": MAX_IMAGE_SIZE_MB,
                "current_size": image.size / (1024 * 1024),
            }
        )


def validate_image_dimensions(image):
    """
    Validates that the image dimensions do not exceed the maximum allowed dimensions.
    """
    if image:
        # Save the current file position
        current_position = image.tell() if hasattr(image, 'tell') else 0
        
        # Open the image to get its dimensions
        try:
            image.seek(0)  # Reset file pointer to the beginning
            with Image.open(image) as img:
                width, height = img.size
                if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
                    raise ValidationError(
                        _(
                            "Image dimensions exceed maximum allowed size of %(max_width)dx%(max_height)d pixels. "
                            "Current size: %(width)dx%(height)d pixels."
                        )
                        % {
                            "max_width": MAX_IMAGE_WIDTH,
                            "max_height": MAX_IMAGE_HEIGHT,
                            "width": width,
                            "height": height,
                        }
                    )
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception:
            # If we can't open the image, it might be invalid
            # But we don't want to raise an error here as Django will handle it
            pass
        finally:
            # Reset file pointer to original position
            if hasattr(image, 'seek'):
                try:
                    image.seek(current_position)
                except (AttributeError, OSError):
                    pass


class Product(BaseModel):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    description = models.TextField(verbose_name=_("Description"))
    market = models.ForeignKey(
        Market,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Market"),
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Discount price"),
    )
    discount_type = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_("Discount type"),
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "main.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Category"),
    )

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        if hasattr(self, "_primary_image_cache"):
            return self._primary_image_cache

        if hasattr(self, "_prefetched_objects_cache") and "images" in self._prefetched_objects_cache:
            images = sorted(
                self._prefetched_objects_cache["images"],
                key=lambda img: (img.position, img.id),
            )
            primary = images[0] if images else None
        else:
            primary = self.images.order_by("position", "id").first()

        self._primary_image_cache = primary
        return self._primary_image_cache

    @property
    def primary_image_file(self):
        primary = self.primary_image
        return primary.image if primary else None

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )
    image = models.ImageField(
        upload_to="product_images/",
        verbose_name=_("Image"),
        validators=[validate_image_size, validate_image_dimensions],
    )
    position = models.PositiveIntegerField(default=0, verbose_name=_("Position"))

    class Meta:
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")
        ordering = ("position", "id")

    def __str__(self):
        return f"{self.product_id}-{self.position}"

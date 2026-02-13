from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image

from apps.main.models import BaseModel, Market

# Image validation constants
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
MAX_IMAGE_WIDTH = 1024
MAX_IMAGE_HEIGHT = 1024


def validate_image_size(image):
    """
    Validates that the image file size does not exceed the maximum allowed size.
    """
    if image.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            "Rasm hajmi %(max_size)s MB dan oshdi. Hozirgi hajmi: %(current_size).2f MB."
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
                        "Rasm o'lchamlari ruxsat etilgan maksimum %(max_width)dx%(max_height)d pikseldan oshdi. "
                        "Hozirgi o'lcham: %(width)dx%(height)d piksel."
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


class CommonProduct(BaseModel):
    name = models.CharField(max_length=128, verbose_name="Nomi")
    description = models.TextField(verbose_name="Tavsif")
    category = models.ForeignKey(
        "main.Category",
        on_delete=models.PROTECT,
        related_name="common_products",
        verbose_name="Kategoriya",
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
        verbose_name = "Umumiy mahsulot"
        verbose_name_plural = "Umumiy mahsulotlar"


class CommonProductImage(BaseModel):
    common_product = models.ForeignKey(
        CommonProduct,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Umumiy mahsulot",
    )
    image = models.ImageField(
        upload_to="common_product_images/",
        verbose_name="Rasm",
        validators=[validate_image_size, validate_image_dimensions],
    )
    position = models.PositiveIntegerField(default=0, verbose_name="O'rin")

    class Meta:
        verbose_name = "Umumiy mahsulot rasmi"
        verbose_name_plural = "Umumiy mahsulot rasmlari"
        ordering = ("position", "id")

    def __str__(self):
        return f"{self.common_product_id}-{self.position}"


class Product(BaseModel):
    common_product = models.ForeignKey(
        CommonProduct,
        on_delete=models.PROTECT,
        related_name="market_products",
        verbose_name="Umumiy mahsulot",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=128, verbose_name="Nomi", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    description = models.TextField(verbose_name="Tavsif", blank=True, null=True)
    market = models.ForeignKey(
        Market,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Do'kon",
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Chegirmali narx",
    )
    discount_type = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Chegirma turi",
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
        verbose_name="Kategoriya",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.resolved_name or "-"

    def clean(self):
        super().clean()
        if not self.common_product:
            errors = {}
            if not self.name:
                errors["name"] = "Umumiy mahsulot tanlanmaganda nomi talab qilinadi."
            if not self.description:
                errors["description"] = "Umumiy mahsulot tanlanmaganda tavsif talab qilinadi."
            if not self.category_id:
                errors["category"] = "Umumiy mahsulot tanlanmaganda kategoriya talab qilinadi."
            if errors:
                raise ValidationError(errors)

    @property
    def resolved_name(self):
        return self.name or (self.common_product.name if self.common_product else None)

    @property
    def resolved_description(self):
        return self.description or (self.common_product.description if self.common_product else None)

    @property
    def resolved_category(self):
        return self.category or (self.common_product.category if self.common_product else None)

    @property
    def primary_image(self):
        if hasattr(self, "_primary_image_cache"):
            return self._primary_image_cache

        primary = None
        if hasattr(self, "_prefetched_objects_cache") and "images" in self._prefetched_objects_cache:
            images = sorted(
                self._prefetched_objects_cache["images"],
                key=lambda img: (img.position, img.id),
            )
            primary = images[0] if images else None
        else:
            primary = self.images.order_by("position", "id").first()

        if not primary and self.common_product:
            primary = self.common_product.primary_image

        self._primary_image_cache = primary
        return self._primary_image_cache

    @property
    def primary_image_file(self):
        primary = self.primary_image
        return primary.image if primary else None

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Mahsulot",
    )
    image = models.ImageField(
        upload_to="product_images/",
        verbose_name="Rasm",
        validators=[validate_image_size, validate_image_dimensions],
    )
    position = models.PositiveIntegerField(default=0, verbose_name="O'rin")

    class Meta:
        verbose_name = "Mahsulot rasmi"
        verbose_name_plural = "Mahsulot rasmlari"
        ordering = ("position", "id")

    def __str__(self):
        return f"{self.product_id}-{self.position}"

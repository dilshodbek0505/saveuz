from django.db import models

from apps.main.models import BaseModel, Product


class Discount(BaseModel):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'ptc', 'Foiz'
        FIXED_AMOUNT = 'fix', "Qat'iy summa"

    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name="discounts",
                                verbose_name="Mahsulot")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Qiymat")
    type = models.CharField(choices=DiscountType.choices, verbose_name="Turi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "Chegirma"
        verbose_name_plural = "Chegirmalar"
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.main.models import BaseModel, Product


class Discount(BaseModel):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'ptc', _('Percentage')
        FIXED_AMOUNT = 'fix', _('Fixed amount')

    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name="discounts",
                                verbose_name=_("Product"))
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Value"))
    type = models.CharField(choices=DiscountType.choices, verbose_name=_("Type"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active ?"))

    def __str__(self):
        return self.product.name
    
    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")
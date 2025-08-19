from django.db import models
from django.utils.translation import gettext_lazy as _ 

from apps.main.models import BaseModel, Market


class Product(BaseModel):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    image = models.ImageField(upload_to="product_images/", verbose_name=_("Image"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    description = models.TextField(verbose_name=_("Description"))
    market = models.ForeignKey(Market,
                               on_delete=models.PROTECT,
                               related_name="products",
                               verbose_name=_("Market"))
    discount_price = models.DecimalField(max_digits=10,
                                         decimal_places=2,
                                         blank=True, null=True,
                                         verbose_name=_("Discount price"))
    discount_type = models.CharField(max_length=128,
                                     blank=True, null=True,
                                     verbose_name=_("Discount type"))
    discount_value = models.DecimalField(max_digits=10,
                                        decimal_places=2,
                                        blank=True, null=True)
    category = models.ForeignKey("main.Category", 
                                 on_delete=models.PROTECT,
                                 related_name="products",
                                 verbose_name=_("Category"))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
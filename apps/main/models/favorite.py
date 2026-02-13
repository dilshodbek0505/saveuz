from django.db import models
from django.contrib.auth import get_user_model

from apps.main.models import BaseModel, Product, Market

User = get_user_model()


class Favorite(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                blank=True, null=True,
                                related_name="favorites")
    market = models.ForeignKey(Market,
                               on_delete=models.CASCADE,
                               blank=True, null=True,
                               related_name="favorites")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sevimli"
        verbose_name_plural = "Sevimlilar"
        unique_together = ('user', 'product')

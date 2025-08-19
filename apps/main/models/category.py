from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.main.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    image = models.ImageField(upload_to="category_images/", verbose_name=_("Image"))
    parent = models.ForeignKey("self", on_delete=models.PROTECT, 
                               blank=True, null=True,
                               related_name="children",
                               verbose_name=_("Parent"))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
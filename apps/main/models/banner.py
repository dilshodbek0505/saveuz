from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.main.models import BaseModel

class Banner(BaseModel):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    image = models.ImageField(upload_to="banner_images/", verbose_name=_("Image"))
    position = models.IntegerField(blank=True, null=True, verbose_name=_("Position"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active ?"))

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")
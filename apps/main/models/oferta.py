from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.main.models import BaseModel


class Oferta(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    file = models.FileField(upload_to="oferta_files/", verbose_name=_("File"), null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Oferta")
        verbose_name_plural = _("Ofertas")
        ordering = ['-created_at']


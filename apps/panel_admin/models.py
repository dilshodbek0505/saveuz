from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.main.models import BaseModel


class AdminDevice(BaseModel):
    """Device token managed via Django admin to gate bulk product creation."""

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    token = models.CharField(max_length=255, unique=True, verbose_name=_("Token"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    class Meta:
        verbose_name = _("Admin device")
        verbose_name_plural = _("Admin devices")

    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"

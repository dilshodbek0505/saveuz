from django.db import models

from apps.main.models import BaseModel


class Oferta(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    file = models.FileField(upload_to="oferta_files/", verbose_name="Fayl", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Oferta"
        ordering = ['-created_at']


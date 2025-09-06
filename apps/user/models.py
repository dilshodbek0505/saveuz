from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.user.managers import CustomUserManager


class User(AbstractUser):
    email = None
    username = None

    phone_number = models.CharField(max_length=20, unique=True, verbose_name=_('Phone number'))
    logo = models.ImageField(
        upload_to="user_logo/",
        blank=True, null=True, 
        verbose_name=_("Logo"))
    notification_allowed = models.BooleanField(default=True)
    test_user = models.BooleanField(default=False, help_text="Test uchun foydalanuvchi")
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    
    lang = models.CharField(
        _("Language"),
        max_length=20,
        choices=settings.LANGUAGES,
        default="uz",  # set your system's default here
        help_text=_("Preferred language for the user"),
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number
    
    class Meta:
        swappable = "AUTH_USER_MODEL"
        verbose_name = _('User')
        verbose_name_plural = _('Users')


import uuid


class PendingVerification(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
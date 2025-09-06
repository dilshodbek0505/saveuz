from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Notification(models.Model):
    class NotificationStatus(models.TextChoices):
        active = "active", _("active")
        inactive = "inactive", _("inactive")

    title = models.CharField(max_length=255)
    body = models.TextField(_("Body"))
    additional_data = models.JSONField(null=True, blank=True)
    photo = models.ImageField(upload_to="notifications/", blank=True, null=True)

    receivers = models.ManyToManyField(User, related_name='notifications', blank=True)

    for_all = models.BooleanField(default=False, verbose_name=_("Barcha uchun"))
    status = models.CharField(max_length=10, choices=NotificationStatus.choices, default=NotificationStatus.active)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='user_notifications')
    send_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    firebase_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.notification.title}"

    class Meta:
        unique_together = ('user', 'notification')

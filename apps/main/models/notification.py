from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    class NotificationStatus(models.TextChoices):
        active = "active", "Faol"
        inactive = "inactive", "Nofaol"

    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    body = models.TextField(verbose_name="Matn")
    additional_data = models.JSONField(null=True, blank=True)
    photo = models.ImageField(upload_to="notifications/", blank=True, null=True)

    receivers = models.ManyToManyField(User, related_name='notifications', blank=True)

    for_all = models.BooleanField(default=False, verbose_name="Barcha uchun")
    status = models.CharField(max_length=10, choices=NotificationStatus.choices, default=NotificationStatus.active)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications', verbose_name="Foydalanuvchi")
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='user_notifications', verbose_name="Bildirishnoma")
    send_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan sana")
    is_read = models.BooleanField(default=False, verbose_name="O'qilgan")
    read_at = models.DateTimeField(null=True, blank=True)
    firebase_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.notification.title}"

    class Meta:
        verbose_name = "Foydalanuvchi bildirishnomasi"
        verbose_name_plural = "Foydalanuvchi bildirishnomalari"
        unique_together = ("user", "notification")

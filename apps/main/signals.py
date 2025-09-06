import time
from django.utils import timezone

from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from apps.main.tasks import send_notification_task, send_notification_to_user_task
from apps.main.models import Notification, UserNotification


@receiver(post_save, sender=Notification)
def send_notification_signal(sender, instance: Notification, **kwargs):
    if instance.status == Notification.NotificationStatus.active:
        send_notification_task.delay(instance.id)


@receiver(m2m_changed, sender=Notification.receivers.through)
def handle_receivers_changed(sender, instance: Notification, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        if instance.for_all:
            return

        receivers = instance.receivers.filter(notification_allowed=True, test_user=False)

        for receiver in receivers:
            user_notification, created = UserNotification.objects.get_or_create(
                user=receiver,
                notification=instance,
                defaults={"send_at": timezone.now()}
            )

            if created:
                send_notification_task.delay(instance.id)
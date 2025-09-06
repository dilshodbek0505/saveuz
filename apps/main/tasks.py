from celery import shared_task
from datetime import date, timedelta

from django.db.models import F
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from firebase_admin import messaging

from apps.main.models import Notification, UserNotification


User = get_user_model()



@shared_task(name="send_notification_task")
def send_notification_task(notification_id):
    notification = Notification.objects.get(id=notification_id)

    if notification.for_all:
        receivers = User.objects.filter(notification_allowed=True, test_user=False)
    else:
        receivers = notification.receivers.filter(notification_allowed=True, test_user=False)
    
    if notification.photo:
        photo_url = notification.photo.url
        full_url = f"{settings.HOST}{photo_url}"
    else:
        full_url = None

    
    for receiver in receivers:
        lang = receiver.lang or 'uz'

        title = getattr(notification, f"title_{lang}", notification.title)
        body = getattr(notification, f"body_{lang}", notification.body)

        user_notification, cr = UserNotification.objects.get_or_create(
            user=receiver,
            notification=notification,
            defaults={
                "send_at": timezone.now(),
            }
        )

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=full_url
            ),
            token=receiver.fcm_token,
            data={}
        )

        try:
            response = messaging.send(message)
            user_notification.firebase_response = {"success": response}
        except Exception as e:
            user_notification.firebase_response = {"error": str(e)}
        
        user_notification.save()
    
    return "NOTIFICATION TASK EXECUTED"


@shared_task(name="send_notification_to_user_task")
def send_notification_to_user_task(notification_id, user_id):
    notification = Notification.objects.get(id=notification_id)
    user = User.objects.get(id=user_id)

    if notification.photo:
        photo_url = notification.photo.url
        full_url = f"{settings.HOST}{photo_url}"
    
    else:
        full_url = None
    
    user_notification, cr = UserNotification.objects.get_or_create(
        user=user,
        notification=notification,
        defaults={
            "send_at": timezone.now(),
        }
    )

    message = messaging.Message(
        notification=messaging.Notification(
            title=notification.title,
            body=notification.body,
            image=full_url,
        ),
        token=user.fcm_token,
        data={}
    )

    try:
        response = messaging.send(message)
        user_notification.firebase_response = {"success": response}
    except Exception as e:
        user_notification.firebase_response = {"error": str(e)}
    
    user_notification.save()

    return "NOTIFICATION TASK EXECUTED"
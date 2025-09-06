from rest_framework import serializers

from apps.main.models import UserNotification, Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id",
                  "title",
                  "body",
                  "photo",
                  "created_at")

class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ("id",
                  "notification",
                  "send_at",
                  "is_read")
    
    def to_representation(self, instance):
        self.fields['notification'] = NotificationSerializer
        return super().to_representation(instance)


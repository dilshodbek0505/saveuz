from rest_framework import generics, permissions
from rest_framework.response import Response

from apps.main.models import UserNotification
from apps.main.serializers import UserNotificationSerializer
from apps.user.models import User


class NotificationListView(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user).order_by("-send_at")

class ToggleNotificationAllowedView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        current_notification_allowed = user.notification_allowed
        user.notification_allowed = not current_notification_allowed
        user.save(update_fields=['notification_allowed'])

        return Response({"enabled": user.notification_allowed})

    def get(self, request, *args, **kwargs):
        return Response({"enabled": request.user.notification_allowed})

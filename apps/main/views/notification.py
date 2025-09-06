from rest_framework import generics, permissions

from apps.main.models import UserNotification
from apps.main.serializers import UserNotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user).order_by("-send_at")

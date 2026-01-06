from django.contrib import admin
from apps.main.models import Notification, UserNotification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    icon_name = "notifications"
    list_display = ('id', 'title', 'created_at', 'for_all')
    list_display_links = ('id', 'title')
    list_editable = []


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    icon_name = "notifications_active"
    list_display = ('id', 'user', 'notification', 'send_at', 'is_read')
    list_display_links = ('id', 'user', 'notification')
    list_editable = ['is_read']
    list_filter = ('user__first_name', 'user__last_name', 'user__phone_number')

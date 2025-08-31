from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'status', 'created_at', 'sent_at']
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['recipient', 'message']
    readonly_fields = ['created_at', 'updated_at']

from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'sent_at', 'created_at', 'created_by')
    list_filter = ('published',)
    readonly_fields = ('sent_at', 'created_at')

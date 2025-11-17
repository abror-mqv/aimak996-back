from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class Notification(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    data = models.JSONField(blank=True, null=True)  # опционально
    published = models.BooleanField(default=False)
    city = models.CharField(max_length=128, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.title} - {'PUBLISHED' if self.published else 'DRAFT'}"
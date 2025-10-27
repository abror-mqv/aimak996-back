# notifications/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Notification
from .utils import send_notification_to_all
from django.utils import timezone

@receiver(pre_save, sender=Notification)
def send_notification_on_publish(sender, instance: Notification, **kwargs):
    # если новая запись, old будет None
    if instance.pk:
        try:
            old = Notification.objects.get(pk=instance.pk)
        except Notification.DoesNotExist:
            old = None
    else:
        old = None

    # условие: раньше не было опубликовано, а теперь ставят published=True
    if (old is None and instance.published) or (old is not None and not old.published and instance.published):
        # попытаемся отправить; если упадёт — не мешаем сохранить, но логгируем
        try:
            send_notification_to_all(instance.title, instance.body, data=instance.data or {})
            instance.sent_at = timezone.now()
        except Exception:
            # sent_at не заполняем при ошибке, админ увидит
            pass

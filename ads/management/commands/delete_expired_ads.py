from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ads.models import Ad

class Command(BaseCommand):
    help = "Delete expired ads"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        count = 0

        for ad in Ad.objects.select_related("category").all():
            if ad.category.name.lower() == "каттам":
                lifetime = timedelta(days=5)
            else:
                lifetime = timedelta(days=30)

            if ad.created_at + lifetime < now:
                ad.delete()
                count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {count} expired ads"))
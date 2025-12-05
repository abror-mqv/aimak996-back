from django.core.management.base import BaseCommand
from ads.models import Ad

class Command(BaseCommand):
    help = 'Marks all existing ads as paid (sets is_paid=True)'

    def handle(self, *args, **options):
        # Get all ads that are not marked as paid yet
        ads_to_update = Ad.objects.filter(is_paid=False)
        count = ads_to_update.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No unpaid ads found. Nothing to update.'))
            return

        # Update all unpaid ads
        updated = ads_to_update.update(is_paid=True)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully marked {updated} ads as paid')
        )

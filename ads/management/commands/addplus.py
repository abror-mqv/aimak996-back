from django.core.management.base import BaseCommand
from django.db import transaction
from ads.models import Ad
from typing import Optional


def add_plus_to_phone(phone: str) -> Optional[str]:
    """Add leading + to phone number if it doesn't have one."""
    if not phone:
        return None
    return phone if phone.startswith('+') else f"+{phone}"


class Command(BaseCommand):
    help = "Add leading + to all Ad.contact_phone values that don't have one."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't save changes, just show what would be changed"
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to process in a single batch (default: 1000)"
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        # Get all ads where contact_phone doesn't start with +
        qs = Ad.objects.exclude(contact_phone__startswith='+').only("id", "contact_phone")
        total = qs.count()
        changed = 0

        self.stdout.write(f"Found {total} ads with phone numbers that don't start with +")

        if dry_run and total > 0:
            self.stdout.write("Dry run - no changes will be saved")
            # Show a few examples
            for ad in qs[:5]:
                self.stdout.write(f"  {ad.contact_phone} -> {add_plus_to_phone(ad.contact_phone)}")
            if total > 5:
                self.stdout.write(f"  ... and {total - 5} more")
            return

        buffer = []
        for ad in qs.iterator(chunk_size=batch_size):
            new_phone = add_plus_to_phone(ad.contact_phone)
            if new_phone and new_phone != ad.contact_phone:
                ad.contact_phone = new_phone
                buffer.append(ad)
                
                if len(buffer) >= batch_size:
                    if not dry_run:
                        with transaction.atomic():
                            Ad.objects.bulk_update(buffer, ["contact_phone"])
                    changed += len(buffer)
                    buffer = []
                    self.stdout.write(f"Processed {changed}/{total} records...")

        if buffer:
            if not dry_run:
                with transaction.atomic():
                    Ad.objects.bulk_update(buffer, ["contact_phone"])
            changed += len(buffer)

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {changed} phone numbers"))
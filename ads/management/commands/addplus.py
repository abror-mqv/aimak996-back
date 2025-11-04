#!/usr/bin/env python3
import os
import sys
from typing import Optional, List, Any

# Add the project root to Python path to allow imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aimak996-back.settings')
import django
django.setup()

from django.core.management.base import BaseCommand
from django.db import transaction
from ads.models import Ad


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

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run = options.get("dry_run", False)
        batch_size = options.get("batch_size", 1000)

        try:
            # Get all ads where contact_phone doesn't start with +
            qs = Ad.objects.exclude(contact_phone__startswith='+').only("id", "contact_phone")
            total = qs.count()
            changed = 0

            self.stdout.write("Found {} ads with phone numbers that don't start with +".format(total))

            if dry_run and total > 0:
                self.stdout.write("Dry run - no changes will be saved")
                # Show a few examples
                for ad in qs[:5]:
                    self.stdout.write("  {} -> {}".format(
                        ad.contact_phone, 
                        add_plus_to_phone(ad.contact_phone)
                    ))
                if total > 5:
                    self.stdout.write("  ... and {} more".format(total - 5))
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
                        self.stdout.write("Processed {}/{} records...".format(changed, total))

            if buffer:
                if not dry_run:
                    with transaction.atomic():
                        Ad.objects.bulk_update(buffer, ["contact_phone"])
                changed += len(buffer)

            self.stdout.write(self.style.SUCCESS(
                "Successfully updated {} phone numbers".format(changed)
            ))

        except Exception as e:
            self.stderr.write("Error: {}".format(str(e)))
            sys.exit(1)


if __name__ == "__main__":
    # This allows running the script directly with: python -m ads.management.commands.addplus
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
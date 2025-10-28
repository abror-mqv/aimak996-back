from django.core.management.base import BaseCommand
from django.db import transaction
from ads.models import Ad
import re


def normalize_phone(raw: str) -> str | None:
    if not raw:
        return None
    digits = re.sub(r"\D+", "", raw)
    if digits.startswith("996"):
        if len(digits) == 12:
            return digits
        if len(digits) > 12 and digits[:12].isdigit():
            return digits[:12]
    if digits.startswith("0"):
        rest = digits[1:]
        if len(rest) == 9:
            return "996" + rest
    if len(digits) == 9:
        return "996" + digits
    if len(digits) == 10 and digits.startswith("0"):
        return "996" + digits[1:]
    if len(digits) == 12 and digits.startswith("996"):
        return digits
    return None


class Command(BaseCommand):
    help = "Normalize Ad.contact_phone values to international format (996XXXXXXXXX)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--batch-size", type=int, default=1000)

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        qs = Ad.objects.all().only("id", "contact_phone")
        total = qs.count()
        changed = 0
        invalid = 0

        buffer = []
        for ad in qs.iterator(chunk_size=batch_size):
            normalized = normalize_phone(ad.contact_phone)
            if not normalized:
                invalid += 1
                continue
            if ad.contact_phone != normalized:
                ad.contact_phone = normalized
                buffer.append(ad)
            if len(buffer) >= batch_size:
                if not dry_run:
                    with transaction.atomic():
                        Ad.objects.bulk_update(buffer, ["contact_phone"], batch_size=batch_size)
                changed += len(buffer)
                buffer = []
        if buffer:
            if not dry_run:
                with transaction.atomic():
                    Ad.objects.bulk_update(buffer, ["contact_phone"], batch_size=batch_size)
            changed += len(buffer)

        self.stdout.write(f"Total: {total}")
        self.stdout.write(f"Changed: {changed}")
        self.stdout.write(f"Invalid_or_unhandled: {invalid}")

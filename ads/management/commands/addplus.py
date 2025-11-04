#!/usr/bin/env python3
import os
import sys
import django
from django.conf import settings
from django.db import connection

def setup_django():
    # Add project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    # Minimal Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aimak996-back.settings')
    
    # Configure Django with minimal settings if not already configured
    if not settings.configured:
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': os.getenv('DB_NAME'),
                    'USER': os.getenv('DB_USER'),
                    'PASSWORD': os.getenv('DB_PASSWORD'),
                    'HOST': os.getenv('DB_HOST', 'localhost'),
                    'PORT': os.getenv('DB_PORT', '5432'),
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'ads',
            ],
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        )
    
    # Initialize Django
    django.setup()

def add_plus_to_phone(phone):
    """Add leading + to phone number if it doesn't have one."""
    if not phone:
        return phone
    return phone if phone.startswith('+') else "+" + phone

def main():
    setup_django()
    
    from django.db import connection
    
    # Use raw SQL to avoid model loading issues
    with connection.cursor() as cursor:
        # Count records that need updating
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ads_ad 
            WHERE contact_phone IS NOT NULL 
            AND contact_phone != ''
            AND contact_phone NOT LIKE '+%'
        """)
        total = cursor.fetchone()[0]
        
        if total == 0:
            print("No phone numbers need to be updated.")
            return
            
        print(f"Found {total} phone numbers to update.")
        
        # First, show what would be changed
        cursor.execute("""
            SELECT id, contact_phone 
            FROM ads_ad 
            WHERE contact_phone IS NOT NULL 
            AND contact_phone != ''
            AND contact_phone NOT LIKE '+%'
            LIMIT 5
        """)
        
        print("\nExample changes:")
        for ad_id, phone in cursor.fetchall():
            print(f"  {phone} -> {add_plus_to_phone(phone)}")
        
        if total > 5:
            print(f"  ... and {total - 5} more")
        
        # Ask for confirmation
        confirm = input("\nDo you want to proceed with these changes? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Update cancelled.")
            return
        
        # Perform the update
        print("Updating phone numbers...")
        cursor.execute("""
            UPDATE ads_ad 
            SET contact_phone = '+' || contact_phone 
            WHERE contact_phone IS NOT NULL 
            AND contact_phone != ''
            AND contact_phone NOT LIKE '+%'
        """)
        
        updated = cursor.rowcount
        print(f"Successfully updated {updated} phone numbers.")

if __name__ == "__main__":
    main()

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
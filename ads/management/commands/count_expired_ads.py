from django.core.management.base import BaseCommand
from ads.utils import count_expired_ads, get_expired_ads_by_category, get_ads_expiring_soon


class Command(BaseCommand):
    help = 'Подсчитывает истекшие объявления и показывает статистику'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Показать детальную информацию об истекших объявлениях',
        )
        parser.add_argument(
            '--category',
            action='store_true',
            help='Показать статистику по категориям',
        )
        parser.add_argument(
            '--expiring',
            type=int,
            default=0,
            help='Показать объявления, которые истекут через N дней (0 - не показывать)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Анализ истекших объявлений ==='))
        
        # Основная статистика
        result = count_expired_ads()
        total_expired = result['total_expired_count']
        
        self.stdout.write(
            self.style.WARNING(f'Всего истекших объявлений: {total_expired}')
        )
        
        # Детальная информация
        if options['detailed'] and total_expired > 0:
            self.stdout.write('\n--- Детальная информация ---')
            for ad in result['expired_ads']:
                self.stdout.write(
                    f"ID: {ad['id']}, "
                    f"Категория: {ad['category']}, "
                    f"Телефон: {ad['contact_phone']}, "
                    f"Создано: {ad['created_at'].strftime('%Y-%m-%d %H:%M')}"
                )
        
        # Статистика по категориям
        if options['category']:
            expired_by_category = get_expired_ads_by_category()
            if expired_by_category:
                self.stdout.write('\n--- Статистика по категориям ---')
                for category, count in expired_by_category.items():
                    self.stdout.write(f"{category}: {count} истекших объявлений")
            else:
                self.stdout.write(self.style.SUCCESS('Нет истекших объявлений в категориях'))
        
        # Объявления, которые скоро истекут
        if options['expiring'] > 0:
            soon_expiring = get_ads_expiring_soon(options['expiring'])
            if soon_expiring:
                self.stdout.write(f'\n--- Объявления, истекающие в ближайшие {options["expiring"]} дней ---')
                for ad in soon_expiring:
                    self.stdout.write(
                        f"ID: {ad['id']}, "
                        f"Категория: {ad['category']}, "
                        f"Истекает через: {ad['expires_in_days']} дней"
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Нет объявлений, истекающих в ближайшие {options["expiring"]} дней')
                )
        
        if total_expired == 0:
            self.stdout.write(self.style.SUCCESS('Нет истекших объявлений!'))

from django.utils import timezone
from datetime import timedelta
from .models import Ad


def count_expired_ads():
    """
    Подсчитывает количество объявлений, которые являются кандидатами на удаление
    (истекшие объявления в зависимости от категории)
    """
    expired_count = 0
    expired_ads = []
    
    all_ads = Ad.objects.all()
    
    for ad in all_ads:
        if ad.is_expired():
            expired_count += 1
            expired_ads.append({
                'id': ad.id,
                'contact_phone': ad.contact_phone,
                'category': ad.category.name_kg,
                'created_at': ad.created_at,
                'is_expired': True
            })
    
    return {
        'total_expired_count': expired_count,
        'expired_ads': expired_ads
    }


def get_expired_ads_by_category():
    """
    Возвращает сгруппированную по категориям статистику истекших объявлений
    """
    from categories.models import Category
    
    expired_by_category = {}
    
    for category in Category.objects.all():
        category_ads = Ad.objects.filter(category=category)
        expired_count = sum(1 for ad in category_ads if ad.is_expired())
        
        if expired_count > 0:
            expired_by_category[category.name_kg] = expired_count
    
    return expired_by_category


def get_ads_expiring_soon(days=3):
    """
    Возвращает объявления, которые истекут в ближайшие дни
    """
    soon_expiring_ads = []
    
    for ad in Ad.objects.all():
        if ad.category.name.lower() == "попутка":
            lifetime = timedelta(days=5)
        else:
            lifetime = timedelta(days=30)
        
        expiry_date = ad.created_at + lifetime
        time_until_expiry = expiry_date - timezone.now()
        
        if 0 < time_until_expiry.days <= days:
            soon_expiring_ads.append({
                'id': ad.id,
                'contact_phone': ad.contact_phone,
                'category': ad.category.name_kg,
                'created_at': ad.created_at,
                'expires_in_days': time_until_expiry.days
            })
    
    return soon_expiring_ads

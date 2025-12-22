from django.utils import timezone
from datetime import timedelta
from .models import Ad


def count_expired_ads():
    """
    Подсчитывает количество объявлений, которые являются кандидатами на удаление
    (истекшие объявления в зависимости от категории)
    """
    expired_count = 0
    expired_media_count = 0
    expired_ads = []
    
    all_ads = Ad.objects.all()
    
    for ad in all_ads:
        if ad.is_expired():
            media_count = ad.photos.count()
            expired_count += 1
            expired_media_count += media_count
            expired_ads.append({
                'id': ad.id,
                'contact_phone': ad.contact_phone,
                'category': ad.category.name_kg,
                'created_at': ad.created_at,
                'is_expired': True,
                'media_count': media_count,
            })
    
    return {
        'total_expired_count': expired_count,
        'total_expired_media_count': expired_media_count,
        'expired_ads': expired_ads
    }


def cleanup_expired_ads():
    """
    Удаляет истекшие объявления и связанные медиафайлы.
    Возвращает словарь со статистикой.
    """
    deleted_ads = 0
    deleted_media = 0
    details = []

    for ad in Ad.objects.all():
        if not ad.is_expired():
            continue

        media_count = ad.photos.count()

        # Удаляем фото через delete(), чтобы стерлись файлы с диска
        for photo in ad.photos.all():
            photo.delete()

        ad_id = ad.id
        ad.delete()

        deleted_ads += 1
        deleted_media += media_count
        details.append({
            'id': ad_id,
            'deleted_media': media_count,
        })

    return {
        'deleted_ads': deleted_ads,
        'deleted_media': deleted_media,
        'details': details,
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

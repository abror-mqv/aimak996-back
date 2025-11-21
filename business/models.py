from django.db import models
from django.contrib.auth.models import User
from ads.models import City
from datetime import time
from colorfield.fields import ColorField


def generate_business_pk():
    import random

    digits = "0123456789"
    while True:
        candidate = "".join(random.choices(digits, k=6))
        if not BusinessCard.objects.filter(pk=candidate).exists():
            return candidate


class BusinessCategory(models.Model):
    name_kg = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to='business/category_icons/', blank=True, null=True)
    gradient_start = ColorField(default="#000000")
    gradient_end = ColorField(default="#FFFFFF")

    def __str__(self):
        return self.name_kg


class BusinessCard(models.Model):
    """Основная карточка бизнеса"""
    id = models.CharField(primary_key=True, max_length=6, unique=True, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='business_cards')
    category = models.ForeignKey(BusinessCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_cards')
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=500, blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='business/profile_photos/', blank=True, null=True)
    header_photo = models.ImageField(upload_to='business/header_photos/', blank=True, null=True)
    cta_phone = models.CharField(max_length=20)  # номер для услуги
    additional_phone = models.CharField(max_length=20, blank=True, null=True)
    management_phone = models.CharField(max_length=20, blank=True, null=True)
    price_info = models.CharField(max_length=100, blank=True, null=True)  # может быть "договорная" или пусто
    address_text = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)  # список тегов
    theme_color = ColorField(default="#000000", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.city.name})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = generate_business_pk()
        super().save(*args, **kwargs)


class BusinessSchedule(models.Model):
    """График работы по дням недели"""
    business = models.ForeignKey(BusinessCard, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('business', 'day_of_week')


class BusinessPhoto(models.Model):
    """Дополнительные фото для карусели"""
    business = models.ForeignKey(BusinessCard, on_delete=models.CASCADE, related_name='carousel_photos')
    image = models.ImageField(upload_to='business/carousel_photos/')
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]


class BusinessCatalogItem(models.Model):
    """Элементы каталога товаров/услуг бизнеса"""
    business = models.ForeignKey(BusinessCard, on_delete=models.CASCADE, related_name='catalog_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='business/catalog_photos/', blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.business.name})"

    class Meta:
        ordering = ["position", "id"]
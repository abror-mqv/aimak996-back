from django.contrib import admin
from .models import (
    BusinessCategory,
    BusinessCard,
    BusinessSchedule,
    BusinessPhoto,
    BusinessCatalogItem,
)


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name_kg", "name_ru", "created_at")
    search_fields = ("name_kg", "name_ru")


@admin.register(BusinessCard)
class BusinessCardAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "category", "created_at", "updated_at")
    list_filter = ("city", "category")
    search_fields = ("name", "short_description", "address_text")


@admin.register(BusinessSchedule)
class BusinessScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "business", "day_of_week", "open_time", "close_time", "is_closed")
    list_filter = ("day_of_week", "is_closed")


@admin.register(BusinessPhoto)
class BusinessPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "business")


@admin.register(BusinessCatalogItem)
class BusinessCatalogItemAdmin(admin.ModelAdmin):
    list_display = ("id", "business", "name", "price", "created_at")
    search_fields = ("name",)

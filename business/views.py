from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import (
    BusinessCategory,
    BusinessCard,
    BusinessPhoto,
    BusinessCatalogItem,
)


def abs_url(request, file_field):
    if not file_field:
        return None
    try:
        return request.build_absolute_uri(file_field.url)
    except Exception:
        return None


class BusinessCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = BusinessCategory.objects.all().order_by("name_kg")
        data = [
            {
                "id": c.id,
                "name_kg": c.name_kg,
                "name_ru": c.name_ru,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "icon_url": abs_url(request, c.icon),
                "gradient_start": str(getattr(c, "gradient_start", None)) if hasattr(c, "gradient_start") else None,
                "gradient_end": str(getattr(c, "gradient_end", None)) if hasattr(c, "gradient_end") else None,
            }
            for c in categories
        ]
        return Response(data)


class BusinessCardDetailByPkView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            b = (
                BusinessCard.objects.select_related("city", "category")
                .prefetch_related("carousel_photos", "catalog_items", "schedules")
                .get(pk=pk)
            )
        except BusinessCard.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        schedules = [
            {
                "day_of_week": s.day_of_week,
                "open_time": s.open_time.isoformat() if s.open_time else None,
                "close_time": s.close_time.isoformat() if s.close_time else None,
                "is_closed": s.is_closed,
            }
            for s in b.schedules.all().order_by("day_of_week")
        ]

        data = {
            "pk": b.pk,
            "id": b.pk,
            "name": b.name,
            "short_description": b.short_description,
            "long_description": b.long_description,
            "profile_photo": abs_url(request, b.profile_photo),
            "header_photo": abs_url(request, b.header_photo),
            "theme_color": getattr(b, "theme_color", None),
            "cta_phone": b.cta_phone,
            "additional_phone": b.additional_phone,
            "management_phone": b.management_phone,
            "price_info": b.price_info,
            "address_text": b.address_text,
            "latitude": float(b.latitude) if b.latitude is not None else None,
            "longitude": float(b.longitude) if b.longitude is not None else None,
            "tags": b.tags,
            "city": b.city.name if b.city_id else None,
            "city_id": b.city_id,
            "category": b.category.name_kg if b.category_id else None,
            "category_id": b.category_id,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "updated_at": b.updated_at.isoformat() if b.updated_at else None,
            "photos": [abs_url(request, p.image) for p in b.carousel_photos.all()],
            "catalog_items": [
                {
                    "id": ci.id,
                    "name": ci.name,
                    "description": ci.description,
                    "photo": abs_url(request, ci.photo),
                    "price": ci.price,
                    "created_at": ci.created_at.isoformat() if ci.created_at else None,
                }
                for ci in b.catalog_items.all()
            ],
            "schedules": schedules,
        }
        return Response(data)


class BusinessCardListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = BusinessCard.objects.select_related("city", "category").all().order_by("-created_at")

        city_id = request.query_params.get("city_id")
        category_id = request.query_params.get("category_id")
        if city_id:
            qs = qs.filter(city_id=city_id)
        if category_id:
            qs = qs.filter(category_id=category_id)

        data = []
        for b in qs:
            data.append(
                {
                    "pk": b.pk,
                    "name": b.name,
                    "short_description": b.short_description,
                    "profile_photo": abs_url(request, b.profile_photo),
                }
            )

        return Response(data)


class BusinessCardDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            b = (
                BusinessCard.objects.select_related("city", "category")
                .prefetch_related("carousel_photos", "catalog_items")
                .get(pk=pk)
            )
        except BusinessCard.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        data = {
            "id": b.id,
            "name": b.name,
            "short_description": b.short_description,
            "long_description": b.long_description,
            "profile_photo": abs_url(request, b.profile_photo),
            "header_photo": abs_url(request, b.header_photo),
            "theme_color": getattr(b, "theme_color", None),
            "cta_phone": b.cta_phone,
            "additional_phone": b.additional_phone,
            "management_phone": b.management_phone,
            "price_info": b.price_info,
            "address_text": b.address_text,
            "latitude": float(b.latitude) if b.latitude is not None else None,
            "longitude": float(b.longitude) if b.longitude is not None else None,
            "tags": b.tags,
            "city": b.city.name if b.city_id else None,
            "city_id": b.city_id,
            "category": b.category.name_kg if b.category_id else None,
            "category_id": b.category_id,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "updated_at": b.updated_at.isoformat() if b.updated_at else None,
            "photos": [abs_url(request, p.image) for p in b.carousel_photos.all()],
            "catalog_items": [
                {
                    "id": ci.id,
                    "name": ci.name,
                    "description": ci.description,
                    "photo": abs_url(request, ci.photo),
                    "price": ci.price,
                    "created_at": ci.created_at.isoformat() if ci.created_at else None,
                }
                for ci in b.catalog_items.all()
            ],
        }
        return Response(data)


class BusinessPhotosByCardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        photos = BusinessPhoto.objects.filter(business_id=pk)
        data = [abs_url(request, p.image) for p in photos]
        return Response(data)


class BusinessCatalogItemsByCardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        items = BusinessCatalogItem.objects.filter(business_id=pk).order_by("-created_at")
        data = [
            {
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "photo": abs_url(request, i.photo),
                "price": i.price,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in items
        ]
        return Response(data)

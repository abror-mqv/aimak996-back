from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from users.models import IsAdminOrModerator

from .models import (
    BusinessCategory,
    BusinessCard,
    BusinessPhoto,
    BusinessCatalogItem,
)
from django.shortcuts import get_object_or_404
import json
from django.db import models


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


# ==========================
# Moderation endpoints (IsAuthenticated)
# ==========================

class ModBusinessCategoryCreateView(APIView):
    permission_classes = [IsAdminOrModerator]

    def post(self, request):
        name_kg = request.data.get("name_kg")
        name_ru = request.data.get("name_ru")
        gradient_start = request.data.get("gradient_start")
        gradient_end = request.data.get("gradient_end")
        icon = request.FILES.get("icon")

        if not name_kg or not name_ru:
            return Response({"error": "name_kg и name_ru обязательны"}, status=400)

        cat = BusinessCategory.objects.create(
            name_kg=name_kg,
            name_ru=name_ru,
            gradient_start=gradient_start or "#000000",
            gradient_end=gradient_end or "#FFFFFF",
            icon=icon,
        )
        return Response({"id": cat.id}, status=201)


class ModBusinessCategoryUpdateView(APIView):
    permission_classes = [IsAdminOrModerator]

    def put(self, request, pk):
        cat = get_object_or_404(BusinessCategory, pk=pk)
        cat.name_kg = request.data.get("name_kg", cat.name_kg)
        cat.name_ru = request.data.get("name_ru", cat.name_ru)
        if "gradient_start" in request.data:
            cat.gradient_start = request.data.get("gradient_start") or cat.gradient_start
        if "gradient_end" in request.data:
            cat.gradient_end = request.data.get("gradient_end") or cat.gradient_end
        if "icon" in request.FILES:
            cat.icon = request.FILES["icon"]
        cat.save()
        return Response({"message": "updated"})

    def patch(self, request, pk):
        return self.put(request, pk)


class ModBusinessCategoryDeleteView(APIView):
    permission_classes = [IsAdminOrModerator]

    def delete(self, request, pk):
        cat = get_object_or_404(BusinessCategory, pk=pk)
        cat.delete()
        return Response({"message": "deleted"})


class ModBusinessCardCreateView(APIView):
    permission_classes = [IsAdminOrModerator]

    def post(self, request):
        city_id = request.data.get("city_id")
        category_id = request.data.get("category_id")
        name = request.data.get("name")
        if not all([city_id, name]):
            return Response({"error": "city_id и name обязательны"}, status=400)

        try:
            city_id = int(city_id)
        except ValueError:
            return Response({"error": "city_id должен быть числом"}, status=400)

        card = BusinessCard(
            city_id=city_id,
            category_id=category_id or None,
            name=name,
            short_description=request.data.get("short_description"),
            long_description=request.data.get("long_description"),
            cta_phone=request.data.get("cta_phone") or "",
            additional_phone=request.data.get("additional_phone"),
            management_phone=request.data.get("management_phone"),
            price_info=request.data.get("price_info"),
            address_text=request.data.get("address_text"),
            latitude=request.data.get("latitude") or None,
            longitude=request.data.get("longitude") or None,
        )

        # tags as JSON
        tags_raw = request.data.get("tags")
        if tags_raw:
            try:
                card.tags = json.loads(tags_raw)
            except Exception:
                return Response({"error": "tags должен быть JSON-массивом"}, status=400)

        # theme_color optional
        theme_color = request.data.get("theme_color")
        if theme_color:
            setattr(card, "theme_color", theme_color)

        # photos
        if "profile_photo" in request.FILES:
            card.profile_photo = request.FILES["profile_photo"]
        if "header_photo" in request.FILES:
            card.header_photo = request.FILES["header_photo"]

        card.save()
        return Response({"pk": card.pk}, status=201)


class ModBusinessCardUpdateView(APIView):
    permission_classes = [IsAdminOrModerator]

    def put(self, request, pk):
        card = get_object_or_404(BusinessCard, pk=pk)
        for f in [
            "name", "short_description", "long_description", "cta_phone",
            "additional_phone", "management_phone", "price_info",
            "address_text"
        ]:
            if f in request.data:
                setattr(card, f, request.data.get(f))

        if "city_id" in request.data:
            try:
                card.city_id = int(request.data.get("city_id"))
            except ValueError:
                return Response({"error": "city_id должен быть числом"}, status=400)
        if "category_id" in request.data:
            card.category_id = request.data.get("category_id") or None
        if "latitude" in request.data:
            card.latitude = request.data.get("latitude") or None
        if "longitude" in request.data:
            card.longitude = request.data.get("longitude") or None
        if "tags" in request.data:
            try:
                card.tags = json.loads(request.data.get("tags")) if request.data.get("tags") else None
            except Exception:
                return Response({"error": "tags должен быть JSON-массивом"}, status=400)
        if "theme_color" in request.data:
            setattr(card, "theme_color", request.data.get("theme_color"))

        if "profile_photo" in request.FILES:
            card.profile_photo = request.FILES["profile_photo"]
        if "header_photo" in request.FILES:
            card.header_photo = request.FILES["header_photo"]

        card.save()
        return Response({"message": "updated"})

    def patch(self, request, pk):
        return self.put(request, pk)


class ModBusinessCardDeleteView(APIView):
    permission_classes = [IsAdminOrModerator]

    def delete(self, request, pk):
        card = get_object_or_404(BusinessCard, pk=pk)
        card.delete()
        return Response({"message": "deleted"})


class ModBusinessScheduleSetView(APIView):
    permission_classes = [IsAdminOrModerator]

    def post(self, request, pk):
        card = get_object_or_404(BusinessCard, pk=pk)
        schedules = request.data.get("schedules")
        if schedules is None:
            return Response({"error": "Нужен массив schedules"}, status=400)
        # schedules может прийти как JSON-строка
        if isinstance(schedules, str):
            try:
                schedules = json.loads(schedules)
            except Exception:
                return Response({"error": "schedules должен быть JSON"}, status=400)

        # replace all
        card.schedules.all().delete()
        to_create = []
        for s in schedules:
            try:
                day = int(s.get("day_of_week"))
            except Exception:
                return Response({"error": "day_of_week обязателен и должен быть числом"}, status=400)
            to_create.append({
                "business": card,
                "day_of_week": day,
                "open_time": s.get("open_time") or None,
                "close_time": s.get("close_time") or None,
                "is_closed": bool(s.get("is_closed", False)),
            })
        # bulk create requires model instances
        from .models import BusinessSchedule
        BusinessSchedule.objects.bulk_create([BusinessSchedule(**x) for x in to_create])
        return Response({"message": "schedules set", "count": len(to_create)})


class ModBusinessPhotoAddView(APIView):
    permission_classes = [IsAdminOrModerator]

    def post(self, request, pk):
        card = get_object_or_404(BusinessCard, pk=pk)
        files = request.FILES.getlist("images") or request.FILES.getlist("image")
        if not files:
            return Response({"error": "Пришлите files=images[]"}, status=400)
        created = []
        # append photos to the end based on current max position
        current_max = BusinessPhoto.objects.filter(business=card).aggregate(m=models.Max("position")).get("m") or 0
        pos = current_max + 1
        for f in files:
            p = BusinessPhoto.objects.create(business=card, image=f, position=pos)
            created.append(p.id)
            pos += 1
        return Response({"created_ids": created}, status=201)


class ModBusinessPhotoDeleteView(APIView):
    permission_classes = [IsAdminOrModerator]

    def delete(self, request, photo_id):
        p = get_object_or_404(BusinessPhoto, pk=photo_id)
        p.delete()
        return Response({"message": "deleted"})


class ModBusinessPhotoReplaceView(APIView):
    permission_classes = [IsAdminOrModerator]

    def put(self, request, photo_id):
        p = get_object_or_404(BusinessPhoto, pk=photo_id)
        if "image" not in request.FILES:
            return Response({"error": "Пришлите image файл"}, status=400)
        p.image = request.FILES["image"]
        p.save()
        return Response({"message": "replaced"})


class ModBusinessPhotosReorderView(APIView):
    permission_classes = [IsAdminOrModerator]

    def post(self, request, pk):
        card = get_object_or_404(BusinessCard, pk=pk)
        order = request.data.get("order")
        if isinstance(order, str):
            try:
                order = json.loads(order)
            except Exception:
                return Response({"error": "order должен быть JSON-массивом id"}, status=400)
        if not isinstance(order, list) or not order:
            return Response({"error": "Передайте order: [photo_id, ...]"}, status=400)
        # map id -> position starting from 1
        pos_map = {int(pid): idx + 1 for idx, pid in enumerate(order)}
        photos = BusinessPhoto.objects.filter(business=card, id__in=pos_map.keys())
        for p in photos:
            p.position = pos_map.get(p.id, p.position)
        BusinessPhoto.objects.bulk_update(photos, ["position"])
        return Response({"message": "reordered", "count": photos.count()})


class ModBusinessCatalogItemAddView(APIView):
    permission_classes = [IsAdminOrModerator]

    def post(self, request, pk):
        card = get_object_or_404(BusinessCard, pk=pk)
        name = request.data.get("name")
        if not name:
            return Response({"error": "name обязателен"}, status=400)
        # append to end
        current_max = BusinessCatalogItem.objects.filter(business=card).aggregate(m=models.Max("position")).get("m") or 0
        item = BusinessCatalogItem(
            business=card,
            name=name,
            description=request.data.get("description"),
            price=request.data.get("price"),
            position=current_max + 1,
        )
        if "photo" in request.FILES:
            item.photo = request.FILES["photo"]
        item.save()
        return Response({"id": item.id}, status=201)


class ModBusinessCatalogItemUpdateView(APIView):
    permission_classes = [IsAdminOrModerator]

    def put(self, request, item_id):
        item = get_object_or_404(BusinessCatalogItem, pk=item_id)
        for f in ["name", "description", "price"]:
            if f in request.data:
                setattr(item, f, request.data.get(f))
        if "position" in request.data:
            try:
                item.position = int(request.data.get("position"))
            except Exception:
                return Response({"error": "position должен быть числом"}, status=400)
        if "photo" in request.FILES:
            item.photo = request.FILES["photo"]
        item.save()
        return Response({"message": "updated"})

    def patch(self, request, item_id):
        return self.put(request, item_id)


class ModBusinessCatalogItemDeleteView(APIView):
    permission_classes = [IsAdminOrModerator]

    def delete(self, request, item_id):
        item = get_object_or_404(BusinessCatalogItem, pk=item_id)
        item.delete()
        return Response({"message": "deleted"})


class ModBusinessCatalogReorderView(APIView):
    permission_classes = [IsAdminOrModerator]

    def post(self, request, pk):
        card = get_object_or_404(BusinessCard, pk=pk)
        order = request.data.get("order")
        if isinstance(order, str):
            try:
                order = json.loads(order)
            except Exception:
                return Response({"error": "order должен быть JSON-массивом id"}, status=400)
        if not isinstance(order, list) or not order:
            return Response({"error": "Передайте order: [item_id, ...]"}, status=400)
        pos_map = {int(iid): idx + 1 for idx, iid in enumerate(order)}
        items = BusinessCatalogItem.objects.filter(business=card, id__in=pos_map.keys())
        for it in items:
            it.position = pos_map.get(it.id, it.position)
        BusinessCatalogItem.objects.bulk_update(items, ["position"])
        return Response({"message": "reordered", "count": items.count()})


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
            "photos": [
                {
                    "url": abs_url(request, p.image),
                    "pos_id": p.position,
                    "image_id": p.id,
                }
                for p in b.carousel_photos.all()
            ],
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
        data = [
            {
                "url": abs_url(request, p.image),
                "pos_id": p.position,
                "image_id": p.id,
            }
            for p in photos
        ]
        return Response(data)


class BusinessCatalogItemsByCardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        items = BusinessCatalogItem.objects.filter(business_id=pk)
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

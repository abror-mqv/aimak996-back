from django.http import JsonResponse
from django.shortcuts import render

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, authentication
from .models import Ad, AdPhoto, City
from categories.models import Category
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

class CreateAdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        description = request.data.get("description")
        contact_phone = request.data.get("contact_phone")
        category_id = request.data.get("category")
        city_ids_raw = request.data.get("cities")

        if not all([description, contact_phone, category_id, city_ids_raw]):
            return Response({"error": "All fields are required"}, status=400)

        # 🔄 Преобразуем "3,6,2" в [3, 6, 2]
        try:
            city_ids = [int(cid.strip()) for cid in city_ids_raw.split(",") if cid.strip().isdigit()]
        except ValueError:
            return Response({"error": "Invalid city IDs"}, status=400)

        # Получаем категорию
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Invalid category"}, status=400)

        # Получаем города
        cities = City.objects.filter(id__in=city_ids)
        if not cities.exists():
            return Response({"error": "No valid cities found"}, status=400)

        # Создаём объявление
        ad = Ad.objects.create(
            description=description,
            contact_phone=contact_phone,
            category=category,
            author=request.user
        )   

        ad.cities.set(cities)

        # Добавляем фото
        for image in request.FILES.getlist("images"):
            AdPhoto.objects.create(ad=ad, image=image)

        return Response({"message": "Ad created", "ad_id": ad.id}, status=201)




class CitiesListView(View):
    def get(self, request):
        cities = City.objects.all().order_by('name')
        data = [{"id": city.id, "name": city.name} for city in cities]
        return JsonResponse(data, safe=False)

class AdsByCityView(View):
    def get(self, request, city_id):
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return JsonResponse({"detail": "Город не найден"}, status=404)

        ads = Ad.objects.filter(cities=city).select_related('category').prefetch_related('photos').order_by('-created_at')

        ads_data = []
        for ad in ads:
            ads_data.append({
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.title if ad.category else None,
                "created_at": ad.created_at.isoformat(),
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

        return JsonResponse(ads_data, safe=False)
    

class AdsByCityAndCategoryView(View):
    def get(self, request, city_id, category_id):
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return JsonResponse({"detail": "Город не найден"}, status=404)

        ads_query = Ad.objects.filter(cities=city)\
                              .select_related('category')\
                              .prefetch_related('photos')\
                              .order_by('-created_at')

        if category_id != 0:
            try:
                category = Category.objects.get(id=category_id)
                ads_query = ads_query.filter(category=category)
            except Category.DoesNotExist:
                return JsonResponse({"detail": "Категория не найдена"}, status=404)

        ads_data = []
        for ad in ads_query:
            cities = ad.cities.all()
            ads_data.append({
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.title,
                "created_at": ad.created_at.isoformat(),
                "category_id": ad.category.id,
                "cities": [city.name for city in cities],
                "cities_ids": [city.id for city in cities],
                "author": ad.author.name,
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

        return JsonResponse(ads_data, safe=False)
    


class AdsByCityAndCategoryViewMine(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, city_id, category_id):
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return Response({"detail": "Город не найден"}, status=404)

        ads_query = Ad.objects.filter(cities=city)\
                              .select_related('category')\
                              .prefetch_related('photos', 'cities')\
                              .order_by('-created_at')

        if category_id != 0:
            try:
                category = Category.objects.get(id=category_id)
                ads_query = ads_query.filter(category=category)
            except Category.DoesNotExist:
                return Response({"detail": "Категория не найдена"}, status=404)

        # 🔒 Только объявления текущего пользователя
        ads_query = ads_query.filter(author=request.user)

        ads_data = []
        for ad in ads_query:
            cities = ad.cities.all()
            ads_data.append({
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.title,
                "category_id": ad.category.id,
                "cities": [city.name for city in cities],
                "cities_ids": [city.id for city in cities],
                "created_at": ad.created_at.isoformat(),
                "author": ad.author.name if ad.author is not None else None,
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

        return Response(ads_data)





class EditAdView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ad_id):
        ad = get_object_or_404(Ad, id=ad_id)

        # Только автор или шеф может редактировать
        if ad.author != request.user and not request.user.is_superuser:
            return Response({"error": "Вы не можете редактировать это объявление"}, status=403)

        # Обновляем поля (только если они переданы)
        ad.description = request.data.get("description", ad.description)
        ad.contact_phone = request.data.get("contact_phone", ad.contact_phone)

        category_id = request.data.get("category")
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                ad.category = category
            except Category.DoesNotExist:
                return Response({"error": "Неверная категория"}, status=400)

        city_ids = request.data.getlist("cities")
        if city_ids:
            try:
                cities = City.objects.filter(id__in=city_ids)
                if not cities.exists():
                    raise ValueError
                ad.cities.set(cities)
            except:
                return Response({"error": "Неверные города"}, status=400)

        # Если переданы новые фотографии — удаляем старые и добавляем новые
        if request.FILES.getlist("images"):
            ad.photos.all().delete()
            for image in request.FILES.getlist("images"):
                AdPhoto.objects.create(ad=ad, image=image)

        ad.save()

        return Response({"message": "Объявление обновлено"}, status=200)
    

class PublicAdsByCityAndCategoryView(View):
    def get(self, request, city_id, category_id):
        # Формируем оптимизированный QuerySet
        ads_query = Ad.objects.select_related('category')\
                             .prefetch_related('photos')\
                             .filter(cities__id=city_id)\
                             .order_by('-created_at')

        if category_id != 0:
            ads_query = ads_query.filter(category_id=category_id)

        # Если нет объявлений, проверяем причину
        if not ads_query.exists():
            if not City.objects.filter(id=city_id).exists():
                return JsonResponse({"detail": "Город не найден"}, status=404)
            if category_id != 0 and not Category.objects.filter(id=category_id).exists():
                return JsonResponse({"detail": "Категория не найдена"}, status=404)

        # Формируем ответ
        ads_data = [{
            "id": ad.id,
            "description": ad.description,
            "contact_phone": ad.contact_phone,
            "category": ad.category.title,
            "created_at": ad.created_at.isoformat(),
            "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
        } for ad in ads_query]

        return JsonResponse(ads_data, safe=False)
    


class AdSearchView(View):
    def get(self, request, city_id):
        query = request.GET.get('q', '').strip()

        # Проверка: город существует?
        if not City.objects.filter(id=city_id).exists():
            return JsonResponse({"detail": "Город не найден"}, status=404)

        # Базовый запрос по городу
        ads_query = Ad.objects.select_related('category')\
                              .prefetch_related('photos')\
                              .filter(cities__id=city_id)\
                              .order_by('-created_at')

        # Если есть поисковый текст — фильтруем
        if query:
            ads_query = ads_query.filter(description__icontains=query)

        ads_data = [{
            "id": ad.id,
            "description": ad.description,
            "contact_phone": ad.contact_phone,
            "category": ad.category.title,
            "created_at": ad.created_at.isoformat(),
            "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
        } for ad in ads_query[:50]]  # ограничим, чтобы не грузить всё подряд

        return JsonResponse(ads_data, safe=False)
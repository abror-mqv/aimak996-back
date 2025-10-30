from django.http import JsonResponse
from django.shortcuts import render

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, authentication
from .models import Ad, AdPhoto, City
from categories.models import Category
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.contrib.auth import get_user_model
from users.models import ModeratorActivityStat
from django.utils import timezone
import pytz


class CreateAdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        description = request.data.get("description")
        contact_phone = request.data.get("contact_phone")
        category_id = request.data.get("category")
        city_ids_raw = request.data.get("cities")

        if not all([description, contact_phone, category_id, city_ids_raw]):
            return Response({"error": "All fields are required"}, status=400)
        try:
            city_ids = [int(cid.strip()) for cid in city_ids_raw.split(",") if cid.strip().isdigit()]
        except ValueError:
            return Response({"error": "Invalid city IDs"}, status=400)
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Invalid category"}, status=400)
        cities = City.objects.filter(id__in=city_ids)
        if not cities.exists():
            return Response({"error": "No valid cities found"}, status=400)
        ad = Ad.objects.create(
            description=description,
            contact_phone=contact_phone,
            category=category,
            author=request.user
        )   
        ad.cities.set(cities)
        for image in request.FILES.getlist("images"):
            AdPhoto.objects.create(ad=ad, image=image)

        
        now = timezone.now().astimezone(pytz.timezone('Asia/Bishkek'))
        date = now.date()
        hour = now.hour

        stat_obj, created = ModeratorActivityStat.objects.get_or_create(
            user=request.user,
            date=date,
            hour=hour,
            defaults={'ad_count': 1}
        )
        if not created:
            stat_obj.ad_count += 1
            stat_obj.save()


            

        return Response({"message": "Ad created", "ad_id": ad.id}, status=201)




class CitiesListView(View):
    def get(self, request):
        cities = City.objects.all().order_by('name')
        data = [{"id": city.id, "name": city.name, "info": {
            "moderator_phone": city.moderator_phone,
            "text_for_share": city.text_for_share,
            "text_for_upload": city.text_for_upload,
            "playmarket_link": city.playmarket_link,
            "appstore_link": city.appstore_link,
            "update_text": city.update_text,
            "required_version": city.required_version,
        }} for city in cities]
        return JsonResponse(data, safe=False)

class UpdateCityInfoView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, city_id):
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return Response({"detail": "Город не найден"}, status=404)
        
        city.moderator_phone = request.data.get("moderator_phone", city.moderator_phone)
        city.text_for_share = request.data.get("text_for_share", city.text_for_share)
        city.text_for_upload = request.data.get("text_for_upload", city.text_for_upload)
        city.playmarket_link = request.data.get("playmarket_link", city.playmarket_link)
        city.appstore_link = request.data.get("appstore_link", city.appstore_link)
        city.update_text = request.data.get("update_text", city.update_text)
        city.required_version = request.data.get("required_version", city.required_version)
        city.save()
        return Response({"detail": "Информация о городе успешно обновлена"}, status=200)

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
                "category": ad.category.name_kg if ad.category else None,
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
                "category": ad.category.name_kg,
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
                "category": ad.category.name_kg if ad.category else None,
                "category_id": ad.category.id,
                "cities": [city.name for city in cities],
                "cities_ids": [city.id for city in cities],
                "created_at": ad.created_at.isoformat(),
                "author": ad.author.name if ad.author is not None else None,
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

        return Response(ads_data)




class DeleteAdView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, ad_id):
        ad = get_object_or_404(Ad, id=ad_id)

        # Только автор или суперюзер может удалить
        if ad.author != request.user and not request.user.is_superuser:
            return Response({"error": "Вы не можете удалить это объявление"}, status=403)

        ad.delete()
        return Response({"message": "Объявление удалено"}, status=200)

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

        # Параметры пагинации
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        paginator = Paginator(ads_query, limit)
        try:
            ads_page = paginator.page(page)
        except EmptyPage:
            ads_page = []

        ads_data = [
            {
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.name_kg if ad.category else None,
                "created_at": ad.created_at.isoformat(),
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            }
            for ad in ads_page
        ]

        return JsonResponse({
            "results": ads_data,
            "page": page,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count
        }, safe=False)
    


class AdSearchView(View):
    def get(self, request, city_id):
        query = request.GET.get('q', '').strip().lower()
        print("123123")

        # Проверка: город существует?
        if not City.objects.filter(id=city_id).exists():
            return JsonResponse({"detail": "Город не найден"}, status=404)

        # Базовый запрос по городу
        ads_query = Ad.objects.select_related('category')\
                              .prefetch_related('photos')\
                              .filter(cities__id=city_id)\
                              .order_by('-created_at')

        # Фильтрация вручную по описанию и телефону
        if query:
            ads_query = [
                ad for ad in ads_query
                if query in (ad.description or '').lower() or query in (ad.contact_phone or '').lower()
            ]
        else:
            ads_query = list(ads_query)

        ads_data = [{
            "id": ad.id,
            "description": ad.description,
            "contact_phone": ad.contact_phone,
            "category": ad.category.name_kg if ad.category else None,
            "created_at": ad.created_at.isoformat(),
            "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
        } for ad in ads_query[:30]]  # Ограничение на первые 50 объявлений

        return JsonResponse(ads_data, safe=False)
    

User = get_user_model()


class AdsByModeratorView(View):
    def get(self, request, moderator_id):
        # Только суперюзер может смотреть чужие объявления
        # if not request.user.is_superuser:
        #     return JsonResponse({"detail": "Доступ запрещён"}, status=403)

        try:
            moderator = User.objects.get(id=moderator_id, is_staff=True)
        except User.DoesNotExist:
            return JsonResponse({"detail": "Модератор не найден"}, status=404)

        # Фильтры
        city_id = request.GET.get("city_id")
        category_id = request.GET.get("category_id")

        ads_query = Ad.objects.filter(author=moderator).select_related('category').prefetch_related('photos', 'cities')

        if city_id:
            ads_query = ads_query.filter(cities__id=city_id)

        if category_id:
            ads_query = ads_query.filter(category__id=category_id)

        ads_query = ads_query.order_by('-created_at')

        ads_data = []
        cities_set = set()

        for ad in ads_query:
            ad_cities = ad.cities.all()
            ads_data.append({
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.name_kg if ad.category else None,
                "category_id": ad.category.id if ad.category else None,
                "cities": [city.name for city in ad_cities],
                "cities_ids": [city.id for city in ad_cities],
                "created_at": ad.created_at.isoformat(),
                "author": ad.author.name if ad.author else None,
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

            # Собираем уникальные города
            for city in ad_cities:
                cities_set.add((city.id, city.name))

        # Преобразуем в список словарей
        cities_list = [{"id": cid, "name": cname} for cid, cname in cities_set]

        return JsonResponse({
            "ads": ads_data,
            "cities": cities_list,
            "moderator_name": moderator.name or moderator.phone
        })
    



class AdsByCityAndCategoryViewMineSearch(APIView):
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

        # Обработка параметра поиска вручную (в Python)
        search_query = request.GET.get('search', '').strip().lower()
        filtered_ads = []
        for ad in ads_query:
            description = ad.description.lower() if ad.description else ''
            contact_phone = ad.contact_phone.lower() if ad.contact_phone else ''
            if search_query in description or search_query in contact_phone:
                filtered_ads.append(ad)

        ads_data = []
        for ad in filtered_ads:
            cities = ad.cities.all()
            ads_data.append({
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.name_kg if ad.category else None,
                "category_id": ad.category.id,
                "cities": [city.name for city in cities],
                "cities_ids": [city.id for city in cities],
                "created_at": ad.created_at.isoformat(),
                "author": ad.author.name if ad.author else None,
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

        return Response({
            "ads": ads_data,
            "cities": [city.name for city in City.objects.all()],
            "moderator_name": request.user.name or request.user.phone
        })
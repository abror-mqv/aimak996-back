from django.http import JsonResponse
from django.shortcuts import render

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, authentication
from .models import Ad, AdPhoto, City
from categories.models import Category
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.contrib.auth import get_user_model
from users.models import ModeratorActivityStat
from django.utils import timezone
import pytz
import io
from PIL import Image
from django.core.files.base import ContentFile

# Target image size in bytes (300KB)
TARGET_IMAGE_SIZE = 300 * 1024

def format_phone(phone: str) -> str:
    """Format phone number to ensure it starts with a plus sign."""
    if not phone:
        return phone
    return phone if phone.startswith('+') else f"+{phone}"


def compress_image(image, target_size=TARGET_IMAGE_SIZE, quality=85, min_quality=40):
    """
    Compress an image to be under the target_size while maintaining aspect ratio.
    Returns a ContentFile with the compressed image data.
    """
    img = Image.open(image)
    
    # Convert to RGB if image is in RGBA mode (to avoid issues with JPEG)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Start with original size and reduce quality until under target size
    current_quality = quality
    output = io.BytesIO()
    
    while current_quality >= min_quality:
        output.seek(0)
        output.truncate()
        
        # Save with current quality setting
        img.save(output, format='JPEG', quality=current_quality, optimize=True)
        
        # If we're under target size or at minimum quality, we're done
        if output.tell() <= target_size or current_quality <= min_quality:
            break
            
        # Reduce quality for next iteration
        current_quality -= 5
    
    # Create a ContentFile with the compressed image data
    output.seek(0)
    return ContentFile(output.read(), name=image.name)


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
        # Ensure phone number has a leading plus
        formatted_phone = format_phone(contact_phone)
        
        ad = Ad.objects.create(
            description=description,
            contact_phone=formatted_phone,
            category=category,
            author=request.user,
            is_paid=True  # Automatically mark new ads as paid
        )   
        ad.cities.set(cities)
        for image in request.FILES.getlist("images"):
            # Check if image is larger than 50KB before compressing
            if image.size > 50 * 1024:  # Only compress if larger than 50KB
                compressed_image = compress_image(image)
                AdPhoto.objects.create(ad=ad, image=compressed_image)
            else:
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


class CreateDraftAdView(APIView):
    permission_classes = [AllowAny]

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
            
        # Format phone number
        formatted_phone = format_phone(contact_phone)
        
        # Create ad without author (for anonymous users)
        ad = Ad.objects.create(
            description=description,
            contact_phone=formatted_phone,
            category=category,
            is_paid=False  # Draft ads are not paid by default
        )   
        
        # Set cities for the ad
        ad.cities.set(cities)
        
        # Handle image uploads
        for image in request.FILES.getlist("images"):
            if image.size > 50 * 1024:  # Only compress if larger than 50KB
                compressed_image = compress_image(image)
                AdPhoto.objects.create(ad=ad, image=compressed_image)
            else:
                AdPhoto.objects.create(ad=ad, image=image)

        # Update moderator stats if user is authenticated
        if request.user.is_authenticated:
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

        return Response({"message": "Draft ad created", "ad_id": ad.id}, status=201)


class UnpaidAdsView(APIView):
    """
    View to list all unpaid ads (for administrators/moderators only)
    """
    #permission_classes = [IsAdminUser]  # Only accessible by admin users
    
    def get(self, request):
        # Get all unpaid ads with related data to avoid N+1 queries
        ads = Ad.objects.filter(is_paid=False)\
                      .select_related('category')\
                      .prefetch_related('cities', 'photos')\
                      .order_by('-created_at')
        
        # Prepare response data
        data = []
        for ad in ads:
            data.append({
                'id': ad.id,
                'description': ad.description,
                'contact_phone': ad.contact_phone,
                'created_at': ad.created_at,
                'category': {
                    'id': ad.category.id,
                    'name': ad.category.name_kg
                },
                'cities': [{'id': city.id, 'name': city.name} for city in ad.cities.all()],
                'photos': [photo.image.url for photo in ad.photos.all() if photo.image],
                'is_confident': ad.is_confident,
                'author': ad.author.username if ad.author else None
            })
            
        return Response({
            'count': len(data),
            'results': data
        })


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
        # Формируем оптимизированный QuerySet
        ads_query = Ad.objects.select_related('category')\
                             .prefetch_related('photos', 'cities')\
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

        ads_data = []
        for ad in ads_page:
            cities = ad.cities.all()
            ads_data.append({
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.name_kg if ad.category else None,
                "category_id": ad.category.id if ad.category else None,
                "cities": [city.name for city in cities],
                "cities_ids": [city.id for city in cities],
                "created_at": ad.created_at.isoformat(),
                "author": ad.author.name if ad.author else None,
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

        return JsonResponse({
            "results": ads_data,
            "page": page,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count
        }, safe=False)
    


class AdsByCityAndCategoryViewMine(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, city_id, category_id):
        # Формируем оптимизированный QuerySet
        ads_query = Ad.objects.select_related('category')\
                             .prefetch_related('photos', 'cities')\
                             .filter(cities__id=city_id, author=request.user)\
                             .order_by('-created_at')

        if category_id != 0:
            ads_query = ads_query.filter(category_id=category_id)

        # Если нет объявлений, проверяем причину
        if not ads_query.exists():
            if not City.objects.filter(id=city_id).exists():
                return Response({"detail": "Город не найден"}, status=404)
            if category_id != 0 and not Category.objects.filter(id=category_id).exists():
                return Response({"detail": "Категория не найдена"}, status=404)

        # Параметры пагинации
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        paginator = Paginator(ads_query, limit)
        
        try:
            ads_page = paginator.page(page)
        except EmptyPage:
            ads_page = []

        ads_data = []
        for ad in ads_page:
            cities = ad.cities.all()
            ads_data.append({
                "id": ad.id,
                "description": ad.description,
                "contact_phone": ad.contact_phone,
                "category": ad.category.name_kg if ad.category else None,
                "category_id": ad.category.id if ad.category else None,
                "cities": [city.name for city in cities],
                "cities_ids": [city.id for city in cities],
                "created_at": ad.created_at.isoformat(),
                "author": ad.author.name if ad.author else None,
                "images": [request.build_absolute_uri(photo.image.url) for photo in ad.photos.all()],
            })

        return Response({
            "results": ads_data,
            "page": page,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count
        })




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
                             .filter(cities__id=city_id, is_paid=True)\
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
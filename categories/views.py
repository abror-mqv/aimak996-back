from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, CityBoard, PinnedMessage, Contacts
from .serializers import CityBoardSerializer, PinnedMessageSerializer, ContactInfoSerializer

from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db import models
from django.db.models import Q

from ads.models import City
from rest_framework import status

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        data = [{
            "id": cat.id,
            "name": cat.name_kg, 
            "ru_name": cat.ru_name
        } for cat in categories]
        return Response(data)
    

class CityBoardListView(APIView):
    def get(self, request):
        boards = CityBoard.objects.all().order_by('-is_active')
        serializer = CityBoardSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data)
    

class PinnedMessageByCityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        city_id = request.query_params.get("city_id")
        if not city_id:
            return Response({"message": None})

        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return Response({"message": None})

        now = timezone.now()
        pinned_message = (
            PinnedMessage.objects.filter(
                is_active=True,
                cities=city,
            )
            .filter(
                models.Q(starts_at__lte=now) | models.Q(starts_at__isnull=True),
                models.Q(ends_at__gte=now) | models.Q(ends_at__isnull=True),
            )
            .order_by("-created_at")
            .first()
        )

        if pinned_message:
            return Response(PinnedMessageSerializer(pinned_message).data)
        return Response({"message": None})
    

class PinnedMessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        three_months_ago = timezone.now() - timedelta(days=90)
        messages = PinnedMessage.objects.filter(created_at__gte=three_months_ago).order_by('-created_at')
        serializer = PinnedMessageSerializer(messages, many=True)
        return Response(serializer.data)
    

class CreatePinnedMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")
        city_ids = request.data.get("city_ids")  # список ID городов
        lifetime_days = request.data.get("lifetime_days")  # int

        if not text or not city_ids or lifetime_days is None:
            return Response({"error": "Нужны text, city_ids и lifetime_days"}, status=400)

        try:
            lifetime_days = int(lifetime_days)
        except ValueError:
            return Response({"error": "lifetime_days должен быть числом"}, status=400)

        cities = City.objects.filter(id__in=city_ids)
        if not cities.exists():
            return Response({"error": "Неверные ID городов"}, status=400)

        now = timezone.now()
        ends_at = now + timedelta(days=lifetime_days)

        message = PinnedMessage.objects.create(
            text=text,
            is_active=True,
            created_at=now,
            starts_at=now,
            ends_at=ends_at,
        )
        message.cities.set(cities)
        message.save()

        return Response({"message": "Закреплённое сообщение создано", "id": message.id}, status=201)



class DeactivatePinnedMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            message = PinnedMessage.objects.get(pk=pk)
        except PinnedMessage.DoesNotExist:
            return Response({"error": "Сообщение не найдено"}, status=404)

        if not message.is_active:
            return Response({"message": "Сообщение уже деактивировано"}, status=200)

        message.is_active = False
        message.save()

        return Response({"message": "Сообщение деактивировано"}, status=200)

class ContactInfoView(APIView):
    def get(self, request):
        city_id = request.query_params.get('city_id')
        
        if not city_id:
            return Response(
                {"error": "city_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            city = City.objects.get(id=city_id)
            admin_contact = Contacts.objects.filter(is_active=True).first()
            
            if not admin_contact:
                return Response(
                    {"error": "Admin contact not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            data = {
                "admin_phone": admin_contact.admin_phone,
                "city": city
            }
            
            serializer = ContactInfoSerializer(data)
            return Response(serializer.data)
            
        except City.DoesNotExist:
            return Response(
                {"error": "City not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
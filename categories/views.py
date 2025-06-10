from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, CityBoard, PinnedMessage
from .serializers import CityBoardSerializer, PinnedMessageSerializer

from django.utils import timezone
from rest_framework.permissions import AllowAny
from django.db import models
from django.db.models import Q

from ads.models import City

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        data = [{"id": cat.id, "name": cat.title} for cat in categories]
        return Response(data)
    

class CityBoardListView(APIView):
    def get(self, request):
        boards = CityBoard.objects.all().order_by('city')
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
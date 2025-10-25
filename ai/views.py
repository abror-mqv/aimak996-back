from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ads.models import Ad
from categories.models import Category
import requests
import json

FASTAPI_LEARN_URL = "http://localhost:8002/learn/"

# 1. Получить следующее сомнительное объявление
@api_view(['GET'])
def get_next_unconfident_ad(request):
    ad = Ad.objects.filter(is_confident=False).order_by('created_at').first()
    if not ad:
        return Response({"detail": "Нет необработанных объявлений"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "id": ad.id,
        "description": ad.description,
        "contact_phone": ad.contact_phone,
        "category": ad.category.ru_name,
        "category_id": ad.category.id,
        "created_at": ad.created_at
    })

@api_view(['POST'])
def confirm_ad_category(request):
    ad_id = request.data.get("ad_id")
    category_id = request.data.get("category_id")
    try:
        ad = Ad.objects.get(id=ad_id)
    except Ad.DoesNotExist:
        return Response({"error": "Ad not found"}, status=status.HTTP_404_NOT_FOUND)

    # Обновляем категорию и метку confident
    ad.category_id = category_id
    ad.confidence = 1.0  # ставим уверенность вручную
    ad.is_confident = True
    print("SAVING CONFIDENT AD")
    ad.save()

    # Отправляем на FastAPI сервер
    try:
        payload = {
            "id": ad.id,
            "description": ad.description,
            "category_id": ad.category_id,
            "created_at": ad.created_at.isoformat()
        }
        print("SENDING TO FASTAPI 1 ")

        response = requests.post(FASTAPI_LEARN_URL, json=payload, timeout=5)
        print("SENDING TO FASTAPI 2")
        if response.status_code != 200:
            return Response(
                {"message": "Ad confirmed, but failed to send to FastAPI", "fastapi_error": response.text},
                status=status.HTTP_207_MULTI_STATUS
            )
        else:
            fastapi_json = json.loads(response.text)
            return Response(
                {"message": "Ad confirmed and sent to FastAPI", "fastapi_response": fastapi_json},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        return Response(
            {"message": "Ad confirmed, but error sending to FastAPI", "error": str(e)},
            status=status.HTTP_207_MULTI_STATUS
        )

    return Response({"message": "Ad confirmed and sent to FastAPI"}, status=status.HTTP_200_OK)
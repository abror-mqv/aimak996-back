from rest_framework import serializers
from .models import CityBoard, PinnedMessage

class CityBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityBoard
        fields = ['id', 'text', 'is_active', 'created_at', 'starts_at', 'ends_at', 'cities']

class PinnedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PinnedMessage
        fields = ['id', 'text', 'is_active', 'created_at', 'starts_at', 'ends_at', 'cities']
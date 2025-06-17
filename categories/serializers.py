from rest_framework import serializers
from .models import CityBoard, PinnedMessage

class CityBoardSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city', read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = CityBoard
        fields = ['id', 'city_name', 'logo_url', 'is_active', 'playmarket_link', 'appstore_link']

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        elif obj.logo:
            return obj.logo.url
        return None
    

class PinnedMessageSerializer(serializers.ModelSerializer):
    cities = serializers.StringRelatedField(many=True)

    class Meta:
        model = PinnedMessage
        fields = ['id', 'text', 'is_active', 'created_at', 'starts_at', 'ends_at', 'cities']
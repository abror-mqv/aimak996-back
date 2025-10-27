from rest_framework import serializers

class TestPushSerializer(serializers.Serializer):
    title = serializers.CharField()
    body = serializers.CharField()

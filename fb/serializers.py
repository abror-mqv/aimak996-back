from rest_framework import serializers

class TestPushSerializer(serializers.Serializer):
    title = serializers.CharField()
    body = serializers.CharField()
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)

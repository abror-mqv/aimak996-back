from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import TestPushSerializer
from .utils import send_notification_to_all

class TestPushView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = TestPushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        send_notification_to_all(data['title'], data['body'])
        return Response({'status': 'ok'})

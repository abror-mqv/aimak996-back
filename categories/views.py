from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        data = [{"id": cat.id, "name": cat.title} for cat in categories]
        return Response(data)
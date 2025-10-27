from django.urls import path
from .views import TestPushView

urlpatterns = [
    path('test-push/', TestPushView.as_view(), name='test-push'),
]

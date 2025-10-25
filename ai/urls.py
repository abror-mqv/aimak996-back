from django.urls import path
from . import views

urlpatterns = [
    path('tinder/next/', views.get_next_unconfident_ad, name='tinder_next'),
    path('tinder/confirm/', views.confirm_ad_category, name='tinder_confirm'),
]
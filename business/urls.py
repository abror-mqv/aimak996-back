from django.urls import path

from .views import (
    BusinessCategoryListView,
    BusinessCardListView,
    BusinessCardDetailView,
    BusinessCardDetailByPkView,
    BusinessPhotosByCardView,
    BusinessCatalogItemsByCardView,
)


urlpatterns = [
    path("categories/", BusinessCategoryListView.as_view()),
    path("cards/", BusinessCardListView.as_view()),
    path("cards/<str:pk>/", BusinessCardDetailView.as_view()),
    path("cards/<str:pk>/photos/", BusinessPhotosByCardView.as_view()),
    path("cards/<str:pk>/catalog/", BusinessCatalogItemsByCardView.as_view()),
    path("pk/<str:pk>/", BusinessCardDetailByPkView.as_view()),
]


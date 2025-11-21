from django.urls import path

from .views import (
    BusinessCategoryListView,
    BusinessCardListView,
    BusinessCardDetailView,
    BusinessCardDetailByPkView,
    BusinessPhotosByCardView,
    BusinessCatalogItemsByCardView,
    ModBusinessCategoryCreateView,
    ModBusinessCategoryUpdateView,
    ModBusinessCategoryDeleteView,
    ModBusinessCardCreateView,
    ModBusinessCardUpdateView,
    ModBusinessCardDeleteView,
    ModBusinessScheduleSetView,
    ModBusinessPhotoAddView,
    ModBusinessPhotoDeleteView,
    ModBusinessPhotoReplaceView,
    ModBusinessPhotosReorderView,
    ModBusinessCatalogItemAddView,
    ModBusinessCatalogItemUpdateView,
    ModBusinessCatalogItemDeleteView,
    ModBusinessCatalogReorderView,
)


urlpatterns = [
    path("categories/", BusinessCategoryListView.as_view()),
    path("cards/", BusinessCardListView.as_view()),
    path("cards/<str:pk>/", BusinessCardDetailView.as_view()),
    path("cards/<str:pk>/photos/", BusinessPhotosByCardView.as_view()),
    path("cards/<str:pk>/catalog/", BusinessCatalogItemsByCardView.as_view()),
    path("pk/<str:pk>/", BusinessCardDetailByPkView.as_view()),

    # Moderation endpoints (protected)
    path("mod/categories/create/", ModBusinessCategoryCreateView.as_view()),
    path("mod/categories/<int:pk>/edit/", ModBusinessCategoryUpdateView.as_view()),
    path("mod/categories/<int:pk>/delete/", ModBusinessCategoryDeleteView.as_view()),

    path("mod/cards/create/", ModBusinessCardCreateView.as_view()),
    path("mod/cards/<str:pk>/edit/", ModBusinessCardUpdateView.as_view()),
    path("mod/cards/<str:pk>/delete/", ModBusinessCardDeleteView.as_view()),

    path("mod/cards/<str:pk>/schedules/set/", ModBusinessScheduleSetView.as_view()),

    path("mod/cards/<str:pk>/photos/add/", ModBusinessPhotoAddView.as_view()),
    path("mod/photos/<int:photo_id>/delete/", ModBusinessPhotoDeleteView.as_view()),
    path("mod/photos/<int:photo_id>/replace/", ModBusinessPhotoReplaceView.as_view()),
    path("mod/cards/<str:pk>/photos/reorder/", ModBusinessPhotosReorderView.as_view()),

    path("mod/cards/<str:pk>/catalog/add/", ModBusinessCatalogItemAddView.as_view()),
    path("mod/catalog/<int:item_id>/edit/", ModBusinessCatalogItemUpdateView.as_view()),
    path("mod/catalog/<int:item_id>/delete/", ModBusinessCatalogItemDeleteView.as_view()),
    path("mod/cards/<str:pk>/catalog/reorder/", ModBusinessCatalogReorderView.as_view()),
]


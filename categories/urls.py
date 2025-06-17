from django.urls import path
from .views import CategoryListView, CityBoardListView, PinnedMessageListView, ContactInfoView

urlpatterns = [
    path('get/', CategoryListView.as_view(), name='category-list'),
    path('city-boards/', CityBoardListView.as_view(), name='city-board-list'),
    path('pinned-messages/', PinnedMessageListView.as_view(), name='pinned-message-list'),
    path('contact-info/', ContactInfoView.as_view(), name='contact-info'),
    # path('pinned-messages/<int:pk>/', PinnedMessageDetailView.as_view(), name='pinned-message-detail'),
]

from django.urls import path
from .views import CategoryListView, CityBoardListView, ContactInfoView, PinnedMessageByCityView, PinnedMessageListView, CreatePinnedMessageView, DeactivatePinnedMessageView

urlpatterns = [
    path('get', CategoryListView.as_view()),
    path("city-boards/", CityBoardListView.as_view(), name="city-board-list"),
    path("pinned-message/", PinnedMessageByCityView.as_view(), name="pinned-message"),
    path("pinned-message-list/", PinnedMessageListView.as_view(), name="pinned-message-list"),
    path("create-pinned-message/", CreatePinnedMessageView.as_view(), name="create-pinned-message"),
    path("deactivate-pinned-message/<int:pk>/", DeactivatePinnedMessageView.as_view(), name="deactivate-pinned-message"),
    path('contact-info/', ContactInfoView.as_view(), name='contact-info'),
]


from django.urls import path
from .views import CategoryListView, CityBoardListView, PinnedMessageByCityView

urlpatterns = [
    path('get', CategoryListView.as_view()),
    path("city-boards/", CityBoardListView.as_view(), name="city-board-list"),
    path("pinned-message/", PinnedMessageByCityView.as_view(), name="pinned-message"),
]

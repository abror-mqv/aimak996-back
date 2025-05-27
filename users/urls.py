from django.urls import path
from .views import StatsMonthView,  StatsWeekView, StatsTodayView,RegisterView, LoginView, CurrentUserView, CreateModeratorView, ListModeratorsView, DeleteModeratorView, UpdateModeratorView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path('admin/moderators/create/', CreateModeratorView.as_view()),
    path('admin/moderators/', ListModeratorsView.as_view()),
    path('admin/moderators/<int:moderator_id>/delete/', DeleteModeratorView.as_view()),
    path('admin/moderators/<int:moderator_id>/edit/', UpdateModeratorView.as_view()),
    path('admin/stats/today/', StatsTodayView.as_view()),
    path('admin/stats/week/', StatsWeekView.as_view()),
    path('admin/stats/month/', StatsMonthView.as_view()),
]

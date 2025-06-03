from django.urls import path
from .views import CreateAdView, AdSearchView, AdsByCityView, CitiesListView, AdsByCityAndCategoryView, AdsByCityAndCategoryViewMine, EditAdView, PublicAdsByCityAndCategoryView

urlpatterns = [
    path('create/', CreateAdView.as_view()),
    path('get/<int:city_id>', AdsByCityView.as_view()),
    path('get-cities-list', CitiesListView.as_view()),
    path('city/<int:city_id>/category/<int:category_id>/', AdsByCityAndCategoryView.as_view()),
    path('my-city/<int:city_id>/category/<int:category_id>/', AdsByCityAndCategoryViewMine.as_view()),
    path('edit/<int:ad_id>/', EditAdView.as_view()),

    path('public-city/<int:city_id>/category/<int:category_id>/', PublicAdsByCityAndCategoryView.as_view()),
    path('search/<int:city_id>/', AdSearchView.as_view(), name='ad-search'),
]

from django.urls import path
from .views import CreateAdView, CreateDraftAdView, AdSearchView, DeleteAdView, AdsByCityAndCategoryViewMineSearch,  AdsByModeratorView,  AdsByCityView, CitiesListView, AdsByCityAndCategoryView, AdsByCityAndCategoryViewMine, EditAdView, PublicAdsByCityAndCategoryView, UpdateCityInfoView, UnpaidAdsView

urlpatterns = [
    path('create/', CreateAdView.as_view()),
    path('get/<int:city_id>', AdsByCityView.as_view()),
    path('get-cities-list', CitiesListView.as_view()),
    path('update-city-info/<int:city_id>', UpdateCityInfoView.as_view()),
    path('city/<int:city_id>/category/<int:category_id>/', AdsByCityAndCategoryView.as_view()),
    path('my-city/<int:city_id>/category/<int:category_id>/', AdsByCityAndCategoryViewMine.as_view()),
    path('by_moderator/<int:moderator_id>/', AdsByModeratorView.as_view()),
    path('my-ads/<int:city_id>/<int:category_id>/', AdsByCityAndCategoryViewMineSearch.as_view(), name='my-ads-by-city-category'),
    path('edit/<int:ad_id>/', EditAdView.as_view()),
    path('delete/<int:ad_id>/', DeleteAdView.as_view(), name='delete_ad'),

    path('public-city/<int:city_id>/category/<int:category_id>', PublicAdsByCityAndCategoryView.as_view()),
    # support both with and without trailing slash for backward compatibility with mobile client
    path('search/<int:city_id>', AdSearchView.as_view(), name='ad-search-noslash'),
    path('search/<int:city_id>/', AdSearchView.as_view(), name='ad-search'),
    
    # Create draft ad (for anonymous users)
    path('create-draft/', CreateDraftAdView.as_view(), name='create-draft-ad'),
    
    # Admin endpoints
    path('admin/unpaid-ads/', UnpaidAdsView.as_view(), name='admin-unpaid-ads'),
]

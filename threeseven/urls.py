from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('ads/', include('ads.urls')),
    path('categories/', include('categories.urls')),
    path('ai/', include('ai.urls')),
    path('fb/', include('fb.urls'))
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
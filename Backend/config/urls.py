from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/profiles/', include('profiles.urls')),
    path('api/v1/friends/', include('friends.urls')),
    path('api/v1/expenses/', include('expenses.urls')),
    path('api/v1/analysis/', include('analysis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

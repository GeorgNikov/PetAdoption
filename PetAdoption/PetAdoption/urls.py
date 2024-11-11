from PetAdoption import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('PetAdoption.core.urls')),
    path('pets/', include('PetAdoption.pets.urls')),
    path('accounts/', include('PetAdoption.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



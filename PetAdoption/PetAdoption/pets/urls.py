from django.urls import path, include

from .views import AddPetView, pet_details, edit_pet, delete_pet, DashboardView
from PetAdoption import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('add/', AddPetView.as_view(), name='add pet'),
    path('<int:pet_pk>/', include([
        path('details/', pet_details, name='pet details'),
        path('edit/', edit_pet, name='edit pet'),
        path('delete/', delete_pet, name='delete pet'),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
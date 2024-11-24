from django.urls import path, include

from .views import AddPetView, delete_pet, Dashboard, PetDetailView, EditPetView, LikePetView, AdoptionRequestView, \
    AdoptionRequestDeleteView


urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('add/', AddPetView.as_view(), name='add pet'),
    path('<slug:pet_slug>/', include([
        path('', PetDetailView.as_view(), name='pet details'),
        path('edit/', EditPetView.as_view(), name='edit pet'),
        path('adopt/', AdoptionRequestView.as_view(), name='adopt_pet'),
    ])),

    path('<int:pet_pk>/', include([
        path('like/', LikePetView.as_view(), name='like pet'),
        path('delete/', delete_pet, name='delete pet'),
        # path('adopt/', AdoptionRequestView.as_view(), name='adopt_pet'),
    ])),
    path('adoption-request/<int:pk>/delete/', AdoptionRequestDeleteView.as_view(), name='adoption request confirm delete'),
    # path('last_adopted_pets/', last_adopted_pets, name='last adopted pets'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
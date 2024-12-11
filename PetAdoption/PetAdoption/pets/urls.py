from django.urls import path, include

from .views import AddPetView, Dashboard, PetDetailView, EditPetView, LikePetView, AdoptionRequestView, \
    AdoptionRequestDeleteView, PetDeleteView

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('add/', AddPetView.as_view(), name='add pet'),

    path('<slug:pet_slug>/', include([
        path('', PetDetailView.as_view(), name='pet details'),
        path('edit/', EditPetView.as_view(), name='edit pet'),
        path('adopt/', AdoptionRequestView.as_view(), name='adopt_pet'),
        path('delete/', PetDeleteView.as_view(), name='delete pet'),
    ])),

    path('<int:pet_pk>/', include([
        path('like/', LikePetView.as_view(), name='like pet'),
    ])),
    path('adoption-request/<int:pk>/delete/', AdoptionRequestDeleteView.as_view(), name='adoption request confirm delete'),

]

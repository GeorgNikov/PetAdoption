from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_pet, name='add pet'),
    path('<int:pet_pk>/', include([
        path('details/', views.pet_details, name='pet details'),
        path('edit/', views.edit_pet, name='edit pet'),
        path('delete/', views.delete_pet, name='delete pet'),
    ])),
]
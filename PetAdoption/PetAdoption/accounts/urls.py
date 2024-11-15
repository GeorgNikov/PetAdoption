from django.contrib.auth.views import LogoutView
from django.urls import path, include

from PetAdoption.accounts.views import UserLoginView, UserProfileView, UserProfileUpdateView, ShelterProfileView, \
    ShelterEditView, UserProfileRedirectView

urlpatterns = [

    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/<int:pk>/', include([
        path('', UserProfileView.as_view(), name='profile details view'),
       # path('', user_profile_detail_view, name='profile details view'),
        path('edit/', UserProfileUpdateView.as_view(), name='profile edit view'),

    ])),
    path('shelter/<int:pk>/', include([
        path('', ShelterProfileView.as_view(), name='shelter details view'),
        path('edit/', ShelterEditView.as_view(), name='shelter edit view'),
    ]),
    ),

    path('redirect-profile/<int:pk>/', UserProfileRedirectView.as_view(), name='redirect-profile')

]

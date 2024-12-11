from django.contrib.auth.views import LogoutView
from django.urls import path, include

from PetAdoption.accounts.views import UserLoginView, UserProfileView, UserProfileUpdateView, ShelterProfileView, \
    ShelterEditView, UserProfileRedirectView, ShelterProfilePreview, ResetPasswordView, PasswordResetConfirmView, \
    ProfileDeleteView
from PetAdoption.core.views import ShelterRatingView, AdoptionRequestsListView, UpdateAdoptionRequestStatusView

urlpatterns = [

    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/<int:pk>/', include([
        path('', UserProfileView.as_view(), name='profile details view'),
        path('edit/', UserProfileUpdateView.as_view(), name='profile edit view'),
        path('delete/', ProfileDeleteView.as_view(), name='profile delete'),

    ])),
    path('shelter/<int:pk>/', include([
        path('', ShelterProfileView.as_view(), name='shelter details view'),
        # path('rate/', submit_rating, name='submit rating'),
        path('edit/', ShelterEditView.as_view(), name='shelter edit view'),
        path('delete/', ProfileDeleteView.as_view(), name='profile delete'),
        path('preview/', ShelterProfilePreview.as_view(), name='shelter page preview'),
        path('adoption-requests/', AdoptionRequestsListView.as_view(), name='shelter adoption requests'),
        path('adoption-requests/<int:request_pk>/update/', UpdateAdoptionRequestStatusView.as_view(),
             name='update adoption request status'),

    ]),
         ),
    path('shelter/<slug:slug>/', include([
        path('', ShelterProfilePreview.as_view(), name='shelter page preview'),
    ]),

         ),

    path('redirect-profile/<int:pk>/', UserProfileRedirectView.as_view(), name='redirect-profile'),
    path('shelter/<int:adoption_request_pk>/rate/', ShelterRatingView.as_view(), name='submit rating'),

    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('reset-password-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

]

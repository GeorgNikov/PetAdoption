from cloudinary.utils import cloudinary_url
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import UpdateView, CreateView, DetailView, FormView

from PetAdoption.accounts.forms import UserRegistrationForm, UserEditProfileForm, ShelterEditProfileForm
from PetAdoption.accounts.models import UserProfile, ShelterProfile
from PetAdoption.accounts.services.geolocation import get_coordinates
from PetAdoption.accounts.utils import load_cities_and_provinces
from PetAdoption.core.models import ShelterRating
from PetAdoption.pets.models import Pet, AdoptionRequest

UserModel = get_user_model()


# USER PROFILE
class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/user-profile-preview.html'
    context_object_name = 'user_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        # Returns the UserProfile instance for the logged user
        return get_object_or_404(UserProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        adoptions = AdoptionRequest.objects.filter(adopter=self.request.user).order_by('-created_at')[:3]
        context['adoptions'] = adoptions

        # Retrieve rated adoption requests by the user
        rated_adoptions = ShelterRating.objects.filter(
            adopter=self.get_object()
        ).values_list('adoption_request', flat=True)

        context['rated_adoptions'] = rated_adoptions

        context['user_profile'] = self.get_object()  # This is the profile of the logged user
        pets = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
        context['pets'] = pets

        return context


# EDIT USER PROFILE
class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserEditProfileForm
    template_name = 'accounts/edit-profile.html'
    context_object_name = 'user_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        # Retrieve the profile using `pk` from the URL
        profile = get_object_or_404(UserProfile, pk=self.kwargs['pk'])

        # Check if the logged user is the owner of the profile
        if profile.user != self.request.user:
            # Redirect to the user's own profile page if they attempt to edit someone else's profile
            return get_object_or_404(UserProfile, user=self.request.user)

        # Return the profile if the user is the owner
        return profile

    def form_valid(self, form):
        profile = form.save(commit=False)

        excluded_fields = ['phone_number']
        # Check if all specified fields are filled
        fields_to_check = [field for field in form.fields if field not in excluded_fields]
        # Check if all the specified fields are filled
        all_fields_filled = all([
            getattr(profile, field) for field in fields_to_check
        ])

        # Set `completed` to True if all fields are filled
        profile.completed = all_fields_filled

        profile.save()

        if profile.completed:
            messages.success(self.request, 'Your profile has been updated successfully!')
        else:
            messages.error(self.request, 'Please fill in all the fields to complete your profile.')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        city_names, provinces = load_cities_and_provinces()
        context['cities'] = city_names
        context['provinces'] = provinces

        return context

    def get_success_url(self):
        return reverse_lazy('profile details view', kwargs={'pk': self.kwargs.get('pk')})


# DELETE USER PROFILE
class ProfileDeleteView(LoginRequiredMixin, View):
    template_name = 'accounts/userprofile-confirm-delete.html'

    @staticmethod
    def get_profile(pk):
        return UserModel.objects.filter(pk=pk).first()

    @staticmethod
    def check_authorization(request, profile):
        if profile.pk != request.user.pk:
            return False
        return True

    def get(self, request, pk, *args, **kwargs):
        profile = self.get_profile(pk)
        if not profile:
            messages.error(request, "Profile not found.")
            return redirect('index')

        if not self.check_authorization(request, profile):
            messages.error(request, "You are not authorized to delete this profile.")
            return redirect('index')

        return render(request, self.template_name, {'profile': profile})

    def post(self, request, pk, *args, **kwargs):
        profile = self.get_profile(pk)
        if not profile:
            messages.error(request, "Profile not found.")
            return redirect('index')

        if not self.check_authorization(request, profile):
            return HttpResponseForbidden("You are not authorized to delete this profile.")

        # Deactivate the user -> is_active = False, if profile shelter -> completed = False and logout
        profile.is_active = False
        if profile.type_user == "Shelter":
            # Shelter profile will not show in 'shelters' but url is still active
            ShelterProfile.objects.filter(user=profile).update(completed=False)
        profile.save()

        logout(request)

        messages.success(request, "Your profile has been DELETED successfully.")
        return redirect('index')


# REGISTRATION VIEW
class UserRegisterView(CreateView):
    model = UserModel
    form_class = UserRegistrationForm
    template_name = 'core/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)

        messages.success(self.request, "Registration successful. Welcome to PetAdoption!")
        return response

    def get_success_url(self):
        return reverse('index')


# USER LOGIN
class UserLoginView(LoginView):
    template_name = 'core/index.html'

    def get_success_url(self):
        user = self.request.user
        return reverse_lazy('redirect-profile', kwargs={'pk': user.pk})


# SHELTER PROFILE
class ShelterProfileView(LoginRequiredMixin, DetailView):
    model = ShelterProfile
    template_name = 'accounts/shelter-profile-view.html'
    context_object_name = 'shelter_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        # Returns the ShelterProfile instance for the logged user
        return get_object_or_404(ShelterProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        adoption_requests = AdoptionRequest.objects.filter(
            pet__owner=self.request.user,
            status='Pending'
        ).order_by(
            '-created_at'
        )
        context['adoption_requests'] = adoption_requests

        shelter_profile = self.get_object()
        context['shelter_profile'] = shelter_profile  # This is the profile of the logged user

        # Get the shelter's image
        if shelter_profile.image:
            bg_image_url, _ = cloudinary_url(shelter_profile.image.url, quality="auto", crop="fit")
            if bg_image_url:
                context['bg_image_url'] = bg_image_url

        pets = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
        context['pets'] = pets

        return context


# EDIT SHELTER PROFILE
class ShelterEditView(LoginRequiredMixin, UpdateView):
    model = ShelterProfile
    form_class = ShelterEditProfileForm
    template_name = 'accounts/shelter-edit-profile.html'
    context_object_name = 'shelter_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        profile = get_object_or_404(ShelterProfile, pk=self.kwargs['pk'])

        # Check if the logged user is the owner of the profile
        if profile.user != self.request.user:
            # Redirect to the user's own profile page if they attempt to edit someone else's profile
            return get_object_or_404(ShelterProfile, user=self.request.user)

        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        city_names, provinces = load_cities_and_provinces()
        context['cities'] = city_names
        context['provinces'] = provinces

        return context

    def form_valid(self, form):
        profile = form.save(commit=False)

        # Fields to exclude from the completion check
        excluded_fields = ['website', 'phone_number']
        fields_to_check = [field for field in form.fields if field not in excluded_fields]

        all_fields_filled = all([
            bool(getattr(profile, field)) for field in fields_to_check
        ])

        # Set profile completed
        profile.completed = all_fields_filled
        profile.save()

        if profile.completed:
            messages.success(self.request, 'Your profile has been completed successfully!')
        else:
            messages.error(self.request, 'Please fill in all the fields to complete your profile.')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shelter details view', kwargs={'pk': self.kwargs.get('pk')})


# SHELTER PROFILE PREVIEW
class ShelterProfilePreview(DetailView):
    model = ShelterProfile
    template_name = 'accounts/shelter-profile-preview.html'
    context_object_name = 'shelter_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None, *args, **kwargs):
        slug = self.kwargs['slug']

        return get_object_or_404(ShelterProfile, slug=slug)

    def get_context_data(self, **kwargs):
        shelter = self.get_object()
        context = super().get_context_data(**kwargs)

        # Get the shelters average rating
        average_rating = ShelterRating.objects.filter(shelter=shelter.pk).aggregate(Avg('rating'))[
                             'rating__avg'] or 0.00
        average_rating_percent = int((average_rating / 5) * 100)
        context['average_rating'] = average_rating
        context['average_rating_percent'] = average_rating_percent

        # Get the shelters overall average rating
        overall_average_rating = ShelterRating.objects.filter(shelter=shelter.pk).aggregate(Avg('rating'))[
                                     'rating__avg'] or 0.00
        overall_average_rating_percent = int((overall_average_rating / 5) * 100)
        context['overall_average_rating_percent'] = overall_average_rating_percent

        # Get shelter reviews
        reviews = ShelterRating.objects.filter(shelter=shelter.pk, feedback__isnull=False).order_by('-created_at')
        context['total_reviews'] = len(reviews)

        # Process each review to add the percentage rating
        for review in reviews:
            if review.rating is not None:  # Ensure the review has a rating
                review.rating_percent = int((review.rating / 5) * 100)
            else:
                review.rating_percent = 0  # If not rating default: 0

        context['reviews'] = reviews[:5]  # Limit the number of reviews to 5

        # Get the shelters profile
        shelter_profile = self.get_object()
        context['shelter_profile'] = shelter_profile

        # Get the shelters image
        if shelter_profile.image:
            bg_image_url, _ = cloudinary_url(shelter_profile.image.url, quality="auto", crop="fit")
            if bg_image_url:
                context['bg_image_url'] = bg_image_url

        # Fetch coordinates for the shelters address
        latitude, longitude = get_coordinates(shelter_profile.full_address)
        if latitude and longitude:
            context['map_coordinates'] = {
                'latitude': latitude,
                'longitude': longitude,
            }
        else:
            context['map_coordinates'] = None

        return context


# REDIRECT PROFILE
class UserProfileRedirectView(LoginRequiredMixin, View):
    """
        Redirects the user to the appropriate profile view based on their user type.
    """

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user

        # Mapping of user types to their corresponding view names
        user_type_to_view = {
            "Adopter": "profile details view",
            "Shelter": "shelter details view",
        }

        # Check if the user type exists in the mapping
        view_name = user_type_to_view.get(user.type_user)

        if view_name:
            # Redirect to the respective view based on the user type
            return redirect(view_name, pk=user.pk)

        # If no valid user type, show an error message
        messages.error(request, "Invalid user type")
        return redirect('index')


class ResetPasswordView(FormView):
    template_name = 'accounts/reset-password.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    # Send password reset email for all users
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = UserModel.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Generate a token for the password reset link
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

            # Send email
            send_mail(
                subject="Reset Your Password",
                message=f"Click the link below to reset your password:\n{reset_link}",
                from_email=email,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('index')
        except UserModel.DoesNotExist:
            messages.error(request, "No user found with that email.")
            return render(request, self.template_name)


class PasswordResetConfirmView(View):
    template_name = 'accounts/password-reset-confirm.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
            token_generator = PasswordResetTokenGenerator()
            if token_generator.check_token(user, token):
                return render(request, self.template_name, {'valid_token': True, 'user_id': uidb64, 'token': token})
            else:
                messages.error(request, "The reset link is invalid or has expired.")
                return redirect('index')
        except:
            messages.error(request, "Invalid password reset link.")
            return redirect('index')

    def post(self, request, uidb64, token, *args, **kwargs):
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name, {
                'valid_token': True,
                'user_id': uidb64,
                'token': token
            })

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
            token_generator = PasswordResetTokenGenerator()
            if token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully!")
                return redirect('index')
            else:
                messages.error(request, "The reset link is invalid or has expired.")
                return redirect('index')
        except:
            messages.error(request, "An error occurred while resetting your password.")
            return redirect('index')

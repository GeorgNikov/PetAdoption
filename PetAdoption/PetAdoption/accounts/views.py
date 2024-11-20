from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import UpdateView, CreateView, DetailView, FormView

from PetAdoption.accounts.forms import UserRegistrationForm, UserEditProfileForm, ShelterEditProfileForm
from PetAdoption.accounts.models import UserProfile, ShelterProfile
from PetAdoption.pets.models import Pet
from PetAdoption.settings import EMAIL_HOST_USER

UserModel = get_user_model()


# class UserProfileDetailsView(LoginRequiredMixin, UpdateView):
#     model = UserProfile
#     template_name = 'accounts/user-profile-preview.html'
#     context_object_name = 'user_profile'
#     login_url = reverse_lazy('index')
#
#     def get_object(self, queryset=None):
#         # Returns the UserProfile instance for the logged-in user
#         return get_object_or_404(UserProfile, user=self.request.user)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user_profile'] = get_object_or_404(UserProfile, user=self.request.user)
#         context['pk'] = self.kwargs.get('pk')
#         return context
#
#     def dispatch(self, request, *args, **kwargs):
#         # Prevent users from accessing other profiles by checking the ID
#         if kwargs['pk'] != str(self.request.user.pk):
#             return redirect('profile details view')  # or raise a 404 error if preferred
#         return super().dispatch(request, *args, **kwargs)


# USER PROFILE
class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/user-profile-preview.html'
    context_object_name = 'user_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        # Returns the UserProfile instance for the logged-in user
        return get_object_or_404(UserProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.get_object()  # This is the profile of the logged-in user
        pets = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
        context['pets'] = pets
        return context


# class UserProfilePreview(LoginRequiredMixin, DetailView):
#     model = UserProfile
#     template_name = 'accounts/user-profile-preview.html'
#     context_object_name = 'user_profile'
#     login_url = reverse_lazy('index')
#
#
#     def get_object(self, queryset=None, pk=None):
#         # Returns the UserProfile instance for the logged-in user
#         return get_object_or_404(UserProfile, user=self.request.user)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user_profile'] = self.get_object()  # This is the profile of the logged-in user
#         pets = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
#         context['pets'] = pets
#         print(context['pets'])
#         return context


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

        # Check if the logged-in user is the owner of the profile
        if profile.user != self.request.user:
            # Redirect to the user's own profile page if they attempt to edit someone else's profile
            return get_object_or_404(UserProfile, user=self.request.user)

        # Return the profile if the user is the owner
        return profile

    def form_valid(self, form):
        # Save the form but don't commit to the database yet
        profile = form.save(commit=False)

        # Check if all specified fields are filled
        all_fields_filled = all([
            getattr(profile, field) for field in form.fields
        ])

        # Set `completed` to True if all fields are filled, otherwise False
        profile.completed = all_fields_filled
        profile.save()  # Now save to the database

        if profile.completed:
            messages.success(self.request, 'Your profile has been updated successfully!')
        else:
            messages.error(self.request, 'Please fill in all the fields to complete your profile.')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile details view', kwargs={'pk': self.kwargs.get('pk')})


# REGISTRATION VIEW
class UserRegisterView(CreateView):
    model = UserModel
    form_class = UserRegistrationForm
    template_name = 'core/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)

        # Redirect to the appropriate profile page after registration
        return response

    def get_success_url(self):
        user = self.object

        if user.type_user == "Adopter":
            # Fetch the related UserProfile
            profile = getattr(user, "user_profile", None)
        elif user.type_user == "Shelter":
            # Fetch the related ShelterProfile
            profile = getattr(user, "shelter_profile", None)
        else:
            profile = None

        if profile and profile.pk:
            # Redirect to the respective profile page
            if user.type_user == "Adopter":
                return reverse('profile details view', kwargs={'pk': profile.pk})
            elif user.type_user == "Shelter":
                return reverse('shelter details view', kwargs={'pk': profile.pk})
        else:
            # Handle case where profile wasn't created (fallback)
            messages.error(self.request, "Profile creation failed. Please contact support.")
            return reverse('index')


# USER LOGIN
class UserLoginView(LoginView):
    template_name = 'core/index.html'

    def get_success_url(self):
        user = self.request.user
        # Redirect to the profile page after login
        return reverse_lazy('redirect-profile', kwargs={'pk': user.pk})


# SHELTER PROFILE
class ShelterProfileView(LoginRequiredMixin, DetailView):
    model = ShelterProfile
    template_name = 'accounts/shelter-profile-preview.html'
    context_object_name = 'shelter_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        # Returns the ShelterProfile instance for the logged-in user
        return get_object_or_404(ShelterProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shelter_profile'] = self.get_object()  # This is the profile of the logged-in user
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

        if profile.user != self.request.user:
            # Redirect to the user's own profile page if they attempt to edit someone else's profile
            return get_object_or_404(ShelterProfile, user=self.request.user)
        # Return the profile if the user is the owner
        return profile

    def form_valid(self, form):
        # Save the form but don't commit to the database yet
        profile = form.save(commit=False)

        # Check if all specified fields are filled
        all_fields_filled = all([
            getattr(profile, field) for field in form.fields
        ])

        # Set `completed` to True if all fields are filled, otherwise False
        profile.completed = all_fields_filled
        profile.save()

        if profile.completed:
            messages.success(self.request, 'Your profile has been completed successfully!')
        else:
            messages.error(self.request, 'Please fill in all the fields to complete your profile.')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shelter details view', kwargs={'pk': self.kwargs.get('pk')})
        # return reverse_lazy('redirect-profile', kwargs={'pk': self.kwargs.get('pk')})


# SHELTER PROFILE PREVIEW
class ShelterProfilePreview(LoginRequiredMixin, DetailView):
    model = ShelterProfile
    template_name = 'accounts/shelter-profile-preview.html'
    context_object_name = 'shelter_profile'
    login_url = reverse_lazy('index')


    def get_object(self, queryset=None, *args, **kwargs):
        slug = self.kwargs['slug']

        return get_object_or_404(ShelterProfile, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shelter_profile'] = self.get_object()  # This is the profile of the logged-in user
        context['pets'] = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
        return context


# REDIRECT PROFILE
class UserProfileRedirectView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        # Retrieve the user object
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


    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = UserModel.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # You would typically generate a token here for the password reset link
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

            # Send email (replace send_mail with actual configuration)
            send_mail(
                subject="Reset Your Password",
                message=f"Click the link below to reset your password:\n{reset_link}",
                from_email=EMAIL_HOST_USER,
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
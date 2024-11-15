from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, CreateView, DetailView

from PetAdoption.accounts.forms import UserRegistrationForm, UserEditProfileForm, ShelterEditProfileForm
from PetAdoption.accounts.models import UserProfile, ShelterProfile
from PetAdoption.pets.models import Pet

UserModel = get_user_model()


class UserProfileDetailsView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'accounts/user-profile.html'
    context_object_name = 'user_profile'
    login_url = reverse_lazy('index')

    def get_object(self):
        # Returns the UserProfile instance for the logged-in user
        return get_object_or_404(UserProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['userprofile'] = get_object_or_404(UserProfile, user=self.request.user)
        context['pk'] = self.kwargs.get('pk')
        return context

    def dispatch(self, request, *args, **kwargs):
        # Prevent users from accessing other profiles by checking the ID
        if kwargs['pk'] != str(self.request.user.pk):
            return redirect('profile details view')  # or raise a 404 error if preferred
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/user-profile.html'
    context_object_name = 'user_profile'
    login_url = reverse_lazy('index')


    def get_object(self):
        # Returns the UserProfile instance for the logged-in user
        return get_object_or_404(UserProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.get_object()  # This is the profile of the logged-in user
        pets = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
        context['pets'] = pets
        print(context['pets'])
        return context



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


class UserRegisterView(CreateView):
    model = UserModel
    form_class = UserRegistrationForm
    template_name = 'core/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_success_url(self):
        # Redirect to the profile page after registration
        return reverse_lazy('redirect-profile', kwargs={'pk': self.object.pk})
        # if self.object.type_user == "Adopter":
        #     return reverse_lazy('profile details view', kwargs={'pk': self.object.pk})
        # else:
        #     return reverse_lazy('shelter details view', kwargs={'pk': self.object.pk})
        #

class UserLoginView(LoginView):
    template_name = 'core/index.html'

    def get_success_url(self):
        user = self.request.user
        # Redirect to the profile page after registration
        return reverse_lazy('redirect-profile', kwargs={'pk': user.pk})


class ShelterProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/shelter-profile.html'
    context_object_name = 'shelter_profile'
    login_url = reverse_lazy('index')


    def get_object(self):
        # Returns the ShelterProfile instance for the logged-in user
        return get_object_or_404(ShelterProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shelter_profile'] = self.get_object()  # This is the profile of the logged-in user
        pets = Pet.objects.filter(owner=self.request.user).order_by('-created_at')
        context['pets'] = pets
        print(context['pets'])
        return context


class ShelterEditView(LoginRequiredMixin, UpdateView):
    model = ShelterProfile
    form_class = ShelterEditProfileForm
    template_name = 'accounts/shelter-edit-profile.html'
    context_object_name = 'shelter_profile'
    login_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        # Retrieve the profile using `pk` from the URL
        profile = get_object_or_404(ShelterProfile, pk=self.kwargs['pk'])
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
        return reverse_lazy('redirect-profile', kwargs={'pk': self.kwargs.get('pk')})



class UserProfileRedirectView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve the user object
        user = request.user

        # Mapping of user types to their corresponding view names
        user_type_to_view = {
            "Adopter": "profile details view",
            "Shelter": "shelter details view"
        }

        # Check if the user type exists in the mapping
        view_name = user_type_to_view.get(user.type_user)

        if view_name:
            # Redirect to the respective view based on the user type
            return redirect(view_name, pk=user.pk)

        # If no valid user type, show an error message
        messages.error(request, "Invalid user type")
        return redirect('index')
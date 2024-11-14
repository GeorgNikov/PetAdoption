from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DetailView

from PetAdoption.accounts.forms import UserRegistrationForm, UserEditProfileForm
from PetAdoption.accounts.models import UserProfile
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

    # def dispatch(self, request, *args, **kwargs):
    #     # Step 1: Get session key from the browser
    #     browser_session_key = request.session.session_key
    #
    #     # Step 2: Try to retrieve the user's session from the database
    #     try:
    #         user_session = Session.objects.get(session_key=browser_session_key, expire_date__gt=timezone.now())
    #     except Session.DoesNotExist:
    #         # Session is not valid or does not exist in the database
    #         return redirect('index')
    #
    #     # Step 3: Ensure the user’s session data matches
    #     session_data = user_session.get_decoded()
    #     database_user_id = session_data.get('_auth_user_id')
    #
    #     print(browser_session_key)
    #     print(user_session)
    #
    #     if str(request.user.id) != database_user_id:
    #         # Redirect if the session data does not match the logged-in user
    #         return redirect('index')
    #
    #     # Continue with the normal request flow if session matches
    #     return super().dispatch(request, *args, **kwargs)

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


# def profile_detail(request, pk):
#     user = get_object_or_404(UserModel, pk=pk)
#
#     context = {
#         'user': user,
#         'pk': pk
#     }
#
#     return render(request, 'accounts/user-profile.html', context)


# @login_required
# def user_profile_detail_view(request, pk):
#     user = get_object_or_404(UserModel, pk=pk)
#     profile = get_object_or_404(UserProfile, user=user)
#
#     user_form = UserForm(request.POST or None, instance=user)    # instantiate the form
#     profile_form = UserEditProfileForm(request.POST or None, instance=profile) # instantiate the form
#
#
#     if request.method == 'POST':
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             return redirect('user profile')
#
#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'user_profile': profile,
#         'user': user
#     }
#
#     return render(request, 'accounts/user-profile.html', context)


#
# @login_required
# def user_profile_detail_view(request, pk):
#     user = get_object_or_404(UserModel, pk=pk)
#     profile = get_object_or_404(UserProfile, user=user)
#
#     session_key = request.session.session_key
#     session = Session.objects.get(session_key=session_key)
#
#     if session:
#
#         print(session)
#         user_form = UserForm(request.POST or None, instance=user)    # instantiate the form
#         profile_form = UserEditProfileForm(request.POST or None, instance=profile) # instantiate the form
#
#
#         if request.method == 'POST':
#             if user_form.is_valid():
#                 if profile_form.is_valid():
#                     user_form.save()
#                     profile_form.save()
#                     return redirect('profile details view', pk=profile.pk)
#
#         context = {
#             'user_form': user_form,
#             'profile_form': profile_form,
#             'user_profile': profile,
#             'pk': pk
#         }
#
#     else:
#         print(session)
#         return redirect('index')
#
#     return render(request, 'accounts/user-profile.html', context)


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

    # def test_func(self):
    #     profile = get_object_or_404(UserProfile, pk=self.kwargs.get('pk'))
    #     return self.request.user == profile.user

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
        return reverse_lazy('profile details view', kwargs={'pk': self.object.pk})


class UserLoginView(LoginView):
    template_name = 'core/index.html'

    def get_success_url(self):
        # Redirect to the profile page after registration
        return reverse_lazy('profile details view', kwargs={'pk': self.request.user.pk})

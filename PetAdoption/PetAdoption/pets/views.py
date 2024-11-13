from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from PetAdoption.accounts.models import UserProfile
from PetAdoption.pets.forms import AddPetForm
from PetAdoption.pets.models import Pet



# # Dashboard to show all pets and link to add pet.
# def dashboard(request):
#     pets = Pet.objects.all().order_by('-created_at')
#
#     context = {
#         'pets': pets
#     }
#
#     return render(request, 'pets/dashboard.html', context)

# Dashboard to show all pets and link to add pet.
class DashboardView(ListView):
    model = Pet
    template_name = 'pets/dashboard.html'
    context_object_name = 'pets'
    paginate_by = 8
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return self.model.objects.filter(status="Available").order_by('-created_at')

    def get_object(self):
        # Returns the UserProfile instance for the logged-in user
        return get_object_or_404(UserProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['user_profile'] = self.get_object()  # This is the profile of the logged-in user

        return context


# def add_pet(request):
#     form = (request.POST or None)
#     user = get_object_or_404(UserProfile, user=request.user)
#
#     if user.completed == False:
#         print(user.completed)
#         return redirect('profile details view', pk=request.user.pk)
#
#     if form.method == 'POST':
#         if form.is_valid():
#             pet = form.save(commit=False)
#             pet.save()
#             return redirect('pet details view', pet.pk)
#
#         else:
#             print(form.errors)
#
#     context = {
#         'form': form
#     }
#
#     return render(request, 'pets/add-pet.html', context)


class AddPetView(LoginRequiredMixin, CreateView):
    model = Pet
    form_class = AddPetForm
    template_name = 'pets/add-pet.html'
    login_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        # Proceed only if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to add a pet.")
            return redirect(self.login_url)

        # Check if the user has a completed profile
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if not user_profile:
            messages.error(request, "Profile does not exist. Please contact support.")
            return redirect('profile edit view', pk=request.user.pk)

        if not user_profile.completed:
            messages.error(request, "Please complete your profile to add a pet.")
            return redirect('profile edit view', pk=user_profile.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        pet = form.save(commit=False)
        pet.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Pet added successfully!')
        return reverse_lazy('dashboard')


def pet_details(request):
    return render(request, 'pets/pet-details.html')


def edit_pet(request):
    return render(request, 'pets/edit-pet.html')

def delete_pet(request):
    return render(request, 'pets/delete-pet.html')




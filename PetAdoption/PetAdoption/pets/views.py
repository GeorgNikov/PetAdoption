from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from PetAdoption.accounts.models import UserProfile
from PetAdoption.pets.forms import AddPetForm, EditPetForm
from PetAdoption.pets.models import Pet

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


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
    paginate_by = 6
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        queryset = self.model.objects.filter(status="Available").order_by('-created_at')
        for pet in queryset:
            pet.liked = pet.likes.filter(pk=self.request.user.pk).exists()
        return queryset

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


class PetDetailView(DetailView):
    model = Pet
    template_name = 'pets/pet-details.html'
    context_object_name = 'pet'
    slug_url_kwarg = 'pet_slug'
    login_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        # Proceed only if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to view details.")
            return redirect(self.login_url)

        # Check if the user has a completed profile
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if not user_profile:
            messages.error(request, "Profile does not exist. Please contact support.")
            return redirect('profile edit view', pk=request.user.pk)


        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = UserProfile.objects.filter(user=self.request.user).first()
        return context

    get_success_url = reverse_lazy('dashboard')


class EditPetView(LoginRequiredMixin, UpdateView):
    model = Pet
    form_class = EditPetForm
    template_name = 'pets/edit-pet.html'
    context_object_name = 'pet'

    def get_object(self, queryset=None):
        # Use pet_slug instead of pk
        pet_slug = self.kwargs['pet_slug']
        pet = get_object_or_404(Pet, slug=pet_slug)  # Assuming you're using a slug field, or adjust if needed
        if pet.owner != self.request.user:
            messages.error(self.request, "You are not allowed to edit this pet.")
            return redirect('dashboard')  # Redirect to another page, e.g., the dashboard
        return pet


    def get_success_url(self):
        messages.success(self.request, "Pet details updated successfully!")
        return reverse_lazy('pet details', kwargs={'slug': self.object.slug})

def delete_pet(request):
    return render(request, 'pets/delete-pet.html')



# REST FRAMEWORK
class LikePetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pet_pk):
        pet = get_object_or_404(Pet, pk=pet_pk)
        if pet.likes.filter(id=request.user.pk).exists():
            # User has already liked this pet, so unlike it
            pet.likes.remove(request.user)
            liked = False
        else:
            # User has not liked this pet, so add like
            pet.likes.add(request.user)
            liked = True

        return Response({
            'liked': liked,
            'total_likes': pet.likes.count()
        }, status=status.HTTP_200_OK)



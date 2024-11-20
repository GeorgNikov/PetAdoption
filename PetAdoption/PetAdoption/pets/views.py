from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from PetAdoption.accounts.models import UserProfile, ShelterProfile
from PetAdoption.pets.forms import AddPetForm, EditPetForm
from PetAdoption.pets.models import Pet

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from PetAdoption.pets.utils import check_profile_completion, check_user_type


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
        if check_user_type(self.request) == "Shelter":
            shelter_profile = get_object_or_404(ShelterProfile, user=self.request.user)
            return get_object_or_404(ShelterProfile, user=self.request.user)

        elif check_user_type(self.request) == "Adopter":
            user_profile = get_object_or_404(UserProfile, user=self.request.user)
            return get_object_or_404(UserProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if check_user_type(self.request) == "Shelter":
            context['shelter_profile'] = ShelterProfile.objects.get(user=user)
        elif check_user_type(self.request) == "Adopter":
            context['user_profile'] = UserProfile.objects.get(user=user)

        return context

    def dispatch(self, request, *args, **kwargs):
        # Proceed only if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please login to view our pets.")
            return redirect('index')

        # Check if the user has a completed profile
        redirect_url = check_profile_completion(request)
        if redirect_url:
            return redirect_url  # Redirect if the profile is incomplete or doesn't exist


        return super().dispatch(request, *args, **kwargs)


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
        redirect_url = check_profile_completion(request)
        if redirect_url:
            return redirect_url  # Redirect if the profile is incomplete or doesn't exist

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
    template_name = 'pets/pet-details-new.html'
    context_object_name = 'pet'
    slug_url_kwarg = 'pet_slug'
    login_url = reverse_lazy('index')
    get_success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # Proceed only if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to view details.")
            return redirect(self.login_url)

        # Check if the user has a completed profile
        redirect_url = check_profile_completion(request)
        if redirect_url:
            return redirect_url  # Redirect if the profile is incomplete or doesn't exist


        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet_owner = Pet.objects.get(slug=self.kwargs['pet_slug']).owner
        context['shelter_owner_profile'] = ShelterProfile.objects.filter(user=pet_owner).first()
        context['user_user_profile'] = UserProfile.objects.filter(user=pet_owner).first()
        context['user_profile'] = UserProfile.objects.filter(user=self.request.user).first()
        return context




class EditPetView(LoginRequiredMixin, UpdateView):
    model = Pet
    form_class = EditPetForm
    template_name = 'pets/edit-pet-new.html'
    context_object_name = 'pet'

    def get_object(self, queryset=None):
        # Use pet_slug instead of pk
        pet_slug = self.kwargs['pet_slug']
        pet = get_object_or_404(Pet, slug=pet_slug)
        if pet.owner != self.request.user:
            messages.error(self.request, "You are not allowed to edit this pet.")
            return redirect('dashboard')
        return pet


    def get_success_url(self):
        messages.success(self.request, "Pet details updated successfully!")
        return reverse_lazy('pet details', kwargs={'pet_slug': self.object.slug})

def delete_pet(request):
    return render(request, 'pets/delete-pet.html')



# def last_adopted_pets(request):
#     pets = Pet.objects.filter(status="Adopted").exclude(owner=request.user).exclude(status="Available").exclude(status="Pending").order_by('-updated_at')[:4]
#
#     context = {
#         'pets': pets
#     }
#
#     return render(request, 'pets/last-adopted-pets.html', context)
#

# REST FRAMEWORK API
class LikePetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(request, pet_pk):
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

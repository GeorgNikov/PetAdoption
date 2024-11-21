from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.template.base import kwarg_re
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from PetAdoption.accounts.models import UserProfile, ShelterProfile
from PetAdoption.pets.forms import AddPetForm, EditPetForm
from PetAdoption.pets.models import Pet

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from PetAdoption.pets.utils import check_profile_completion, check_user_type


# Dashboard to show all pets and link to add pet. WORKED
# class DashboardView(ListView):
#     model = Pet
#     template_name = 'pets/dashboard.html'
#     context_object_name = 'pets'
#     paginate_by = 6
#     success_url = reverse_lazy('dashboard')
#
#     def get_queryset(self):
#         queryset = self.model.objects.filter(status="Available").order_by('-created_at')
#         for pet in queryset:
#             pet.liked = pet.likes.filter(pk=self.request.user.pk).exists()
#
#         return queryset
#
#     def get_object(self):
#         # Returns the UserProfile instance for the logged-in user
#         if check_user_type(self.request) == "Shelter":
#             shelter_profile = get_object_or_404(ShelterProfile, user=self.request.user)
#             return shelter_profile
#
#         elif check_user_type(self.request) == "Adopter":
#             user_profile = get_object_or_404(UserProfile, user=self.request.user)
#             return user_profile
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         shelter_param = self.request.GET.get('shelter')
#         user = self.request.user
#
#         if shelter_param:
#             # Assuming `shelter_param` corresponds to a field in the ShelterProfile model
#             shelter = get_object_or_404(ShelterProfile, user__pk=shelter_param)
#             context['shelter'] = shelter
#             # Filter pets by shelter
#             pets = Pet.objects.filter(owner=shelter.user.pk, status="Available").order_by('-created_at')
#
#         else:
#             pets = Pet.objects.filter(status="Available").order_by('-created_at')
#
#         for pet in pets:
#             pet.liked = pet.likes.filter(pk=self.request.user.pk).exists()
#
#         if check_user_type(self.request) == "Shelter":
#             context['shelter_profile'] = ShelterProfile.objects.get(user=user)
#         elif check_user_type(self.request) == "Adopter":
#             context['user_profile'] = UserProfile.objects.get(user=user)
#
#             # Paginate the filtered pets
#         paginator = Paginator(pets, 6)  # 10 pets per page
#         page_number = self.request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#
#         context['page_obj'] = page_obj
#         context['pets'] = page_obj.object_list
#         context['paginator'] = paginator
#         context['shelter'] = shelter_param
#
#         return context
#
#     def dispatch(self, request, *args, **kwargs):
#         # Proceed only if the user is authenticated
#         if not request.user.is_authenticated:
#             messages.error(request, "Please login to view our pets.")
#             return redirect('index')
#
#         # Check if the user has a completed profile
#         redirect_url = check_profile_completion(request)
#         if redirect_url:
#             return redirect_url  # Redirect if the profile is incomplete or doesn't exist
#
#
#         return super().dispatch(request, *args, **kwargs)

# TEST NEW DASHBOARD VIEW
class Dashboard(ListView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the request's query parameters
        query_params = self.request.GET.copy()

        # Remove the 'page' parameter from the query parameters
        query_params.pop('page', None)

        # Now pass the cleaned query parameters to the context
        context['query_params'] = query_params.urlencode()

        # Handle other filtering logic like shelter, age, city
        shelter_param = self.request.GET.get('shelter')
        age_param = self.request.GET.get('age')
        city_param = self.request.GET.get('city')

        pets = Pet.objects.filter(status="Available")
        if shelter_param:
            pets = pets.filter(owner__pk=shelter_param)
        if age_param:
            pets = pets.filter(age=age_param)
        if city_param:
            pets = pets.filter(city__iexact=city_param)

        # Paginate the filtered pets
        paginator = Paginator(pets, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Add pagination and pets to the context
        context['pets'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        return context


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

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from PetAdoption.accounts.models import UserProfile, ShelterProfile
from PetAdoption.pets.forms import AddPetForm, EditPetForm, AdoptionRequestForm
from PetAdoption.pets.models import Pet, AdoptionRequest

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from PetAdoption.pets.utils import check_profile_completion


# DASHBOARD VIEW
class Dashboard(ListView):
    model = Pet
    template_name = 'pets/dashboard.html'
    context_object_name = 'pets'
    paginate_by = 6
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        queryset = self.model.objects.filter(status__in=["Available", "Pending"]).order_by('-created_at')

        for pet in queryset:
            pet.liked = pet.likes.filter(pk=self.request.user.pk).exists()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_params = self.request.GET.copy()

        # Remove the 'page' parameter from the query parameters
        query_params.pop('page', None)

        # Now pass the cleaned query parameters to the context
        context['query_params'] = query_params.urlencode()

        # Handle other filtering logic like shelter, age, city
        shelter_param = self.request.GET.get('shelter')
        age_param = self.request.GET.get('age')
        city_param = self.request.GET.get('city')

        pets = Pet.objects.filter(status="Available").order_by('-created_at')
        if shelter_param:
            pets = pets.filter(owner__pk=shelter_param)
        if age_param:
            pets = pets.filter(age=age_param)
        if city_param:
            pets = pets.filter(city__iexact=city_param)

        for pet in pets:
            pet.liked = pet.likes.filter(pk=self.request.user.pk).exists()

        # Paginate the filtered pets
        paginator = Paginator(pets, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Add pagination and pets to the context
        context['pets'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['paginator'] = paginator
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
        """
        Ensure only users with a ShelterProfile can access this page.
        Redirect unauthenticated users or those with a UserProfile to the dashboard page.
        """
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to access this page.")
            return redirect('index')

        # Check if the user has a ShelterProfile
        try:
            shelter_profile = ShelterProfile.objects.get(user=request.user)
        except ShelterProfile.DoesNotExist:
            # If user does not have a ShelterProfile, redirect to index page
            messages.error(request, "You are not authorized to access this page.")
            return redirect('dashboard')

        # If the user has a ShelterProfile, continue with the view
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
    slug_field = 'slug'
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

    def dispatch(self, request, *args, **kwargs):
        """
        Allow access only if the logged-in user matches the owner of the profile in the URL!!!
        """
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to access this page.")
            return redirect('index')

        # Check if the logged-in user's pk matches the pk in the URL
        profile_pk = kwargs.get('pk')  # Get the pk from the URL
        if request.user.pk != profile_pk:
            messages.error(request, "You are not authorized to edit this pet.")
            return redirect('dashboard')

        # Allow access if the checks pass
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Use pet_slug instead of pk
        pet_slug = self.kwargs['pet_slug']
        pet = get_object_or_404(Pet, slug=pet_slug)

        return pet


    def get_success_url(self):
        messages.success(self.request, "Pet details updated successfully!")
        return reverse_lazy('pet details', kwargs={'pet_slug': self.object.slug})


# DELETE PET
class PetDeleteView(LoginRequiredMixin, DeleteView):
    model = Pet
    template_name = 'pets/delete-pet-confirm.html'  # A confirmation template
    slug_field = 'slug'
    success_url = reverse_lazy('dashboard')  # Redirect after deletion

    def get_object(self, queryset=None):
        # Get the pet object and check ownership
        pet = get_object_or_404(Pet, slug=self.kwargs['pet_slug'])
        return pet

    def dispatch(self, request, *args, **kwargs):
        # Get the pet object
        pet = self.get_object()

        # Check if the logged-in user is the owner
        if request.user != pet.owner:
            messages.error(request, "You are not authorized to delete this pet.")
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class AdoptionRequestView(LoginRequiredMixin, CreateView):
    model = AdoptionRequest
    form_class = AdoptionRequestForm
    template_name = 'pets/adoption-request.html'

    # def dispatch(self, request, *args, **kwargs):
    #     adoption_request = get_object_or_404(AdoptionRequest, pk=kwargs['request_pk'], shelter=self.request.user)
    #     print(adoption_request)
    #     # Proceed only if the user is authenticated
    #     if not request.user.is_authenticated:
    #         messages.error(request, "You are not logged-in.")
    #         return redirect('index')
    #     if adoption_request.adopter != request.user:
    #         messages.error(request, "You are not authorized to view adoption request.")
    #         return reverse_lazy('redirect-profile', kwargs={'pk': request.user.pk})
    #
    #     return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        pet_slug = self.kwargs.get('pet_slug')
        pet = get_object_or_404(Pet, slug=pet_slug)

        # Prevent the owner from adopting their own pet
        if pet.owner == self.request.user:
            messages.error(self.request, "You cannot adopt your own pet.")
            return redirect('dashboard')

        # Prevent multiple requests for the same pet
        if AdoptionRequest.objects.filter(adopter=self.request.user, pet=pet).exists():
            messages.error(self.request, "You have already requested to adopt this pet.")
            return redirect('dashboard')

        # Automatically set the adopter and pet for the adoption request
        form.instance.adopter = self.request.user
        form.instance.pet = pet
        pet.status = "Pending"
        pet.save()

        # Save the form and redirect to a success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet_slug = self.kwargs.get('pet_slug')
        pet = get_object_or_404(Pet, slug=pet_slug)
        context['pet'] = get_object_or_404(Pet, slug=pet_slug)  # Pass the pet to the template
        context['shelter_owner_profile'] = ShelterProfile.objects.get(user=pet.owner)
        return context

    def get_success_url(self):
        return reverse_lazy('redirect-profile', kwargs={'pk': self.request.user.pk})



class AdoptionRequestDeleteView(LoginRequiredMixin, DeleteView):
    model = AdoptionRequest
    template_name = 'pets/adoption-request-confirm-delete.html'
    context_object_name = 'request'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to access this page.")
            return redirect('index')

        # Retrieve the pk from kwargs
        pk = kwargs.get('pk')

        # Try to retrieve the AdoptionRequest
        try:
            adoption_request = AdoptionRequest.objects.get(pk=pk)
        except AdoptionRequest.DoesNotExist:
            messages.error(request, "The requested adoption record does not exist.")
            return redirect(reverse_lazy('redirect-profile', kwargs={'pk': request.user.pk}))

        # Check if the logged-in user is the adopter
        if adoption_request.adopter != request.user:
            messages.error(request, "You are not authorized to access this page.")
            return redirect(reverse_lazy('redirect-profile', kwargs={'pk': request.user.pk}))

        # Allow access if the checks pass
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Restore the pet's status to "Available"
        adoption_request = self.get_object()
        pet = adoption_request.pet
        pet.status = "Available"
        pet.save()

        # Redirect the user after deletion
        return reverse_lazy('dashboard')

    def test_func(self):
        # Ensure only the adopter who created the request can delete it
        adoption_request = self.get_object()
        return adoption_request.adopter == self.request.user





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

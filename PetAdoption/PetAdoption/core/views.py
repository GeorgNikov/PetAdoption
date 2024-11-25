from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView

from PetAdoption.accounts.forms import UserLoginForm, UserRegistrationForm
from PetAdoption.accounts.models import ShelterProfile, UserProfile
from PetAdoption.core.forms import ContactForm, ShelterRatingForm
from PetAdoption.core.models import ShelterRating
from PetAdoption.pets.models import Pet, AdoptionRequest
from PetAdoption.pets.utils import check_user_type

UserModel = get_user_model()

def index(request):
    form = UserLoginForm(request.POST or None)
    register_form = UserRegistrationForm(request.POST or None)
    try:
        pets = Pet.objects.filter(
            status="Adopted"
        ).order_by(
            '-updated_at'
        )[:4]
    except:
        pets = []

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")

        elif register_form.is_valid():
            register_form.save()
            username = register_form.cleaned_data.get('username')
            password = register_form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            # return redirect('profile details view', pk=user.pk)

            if check_user_type(request) == "Adopter":
                return redirect('profile details view', pk=user.pk)
            elif check_user_type(request) == "Shelter":
                return redirect('shelter page preview', pk=user.pk)
            return redirect('index')

    context = {
        'form': form,
        'register_form': register_form,
        'pets': pets,
    }

    return render(request, 'core/index.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            # Send an email (optional)
            send_mail(
                subject,
                message,
                email,  # from email
                [settings.CONTACT_EMAIL],  # to email
                fail_silently=False,
            )

            # TODO: Save contact form data to the database model-ContactForm in core

            # Display success message
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect back to the contact page

    else:
        form = ContactForm()

    return render(request, 'core/contacts.html', {'form': form})


class FAQView(TemplateView):
    template_name = 'core/faq.html'


# View to show shelter ratings
# def show_ratings(request, slug):
#     shelter = get_object_or_404(ShelterProfile, slug=slug)
#     ratings = ShelterRating.objects.filter(shelter=shelter.pk).all()
#
#     # Calculate the average rating
#     average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
#
#     # Ensure a fallback value if there are no ratings
#     average_rating = average_rating if average_rating is not None else 0
#
#     context = {
#         'shelter': shelter,
#         'ratings': ratings,
#         'average_rating': average_rating,
#     }
#
#     return render(request, 'core/show-rating.html', context)


class SheltersView(TemplateView):
    model = ShelterProfile
    template_name = 'core/shelters.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shelters = ShelterProfile.objects.all()

        # For each shelter, get the count of available pets
        shelters_with_pet_count = []

        for shelter in shelters:
            # Count the number of available pets for this shelter
            available_pets_count = Pet.objects.filter(owner=shelter.user.pk, status="Available").count()
            average_rating = ShelterRating.objects.filter(shelter=shelter.pk).aggregate(Avg('rating'))['rating__avg'] or 0.00
            average_rating_percent = int((average_rating / 5) * 100)

            shelters_with_pet_count.append({
                'shelter': shelter,
                'available_pets_count': available_pets_count,
                'slug': shelter.slug,
                'average_rating': average_rating,
                'average_rating_percent': average_rating_percent
            })

        # Add the shelter information with the pet count to the context
        context['shelters'] = shelters_with_pet_count

        return context


class ShelterRatingView(LoginRequiredMixin, FormView):
    template_name = 'accounts/shelter-feedback-rating.html'
    form_class = ShelterRatingForm

    def get_user_profile(self):
        return get_object_or_404(UserProfile, user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        # Ensure the user is authorized to rate the shelter
        self.adoption_request = get_object_or_404(
            AdoptionRequest,
            pk=self.kwargs.get('adoption_request_pk'),
            adopter=self.request.user,
            status='Approved'  # Ensure the adoption is approved
        )
        self.shelter = self.adoption_request.pet.owner.shelter_profile  # Get shelter from adoption request

        # Check if the user has already rated the shelter for this adoption request
        if ShelterRating.objects.filter(
                adopter=self.get_user_profile(),
                shelter=self.shelter,
                adoption_request=self.adoption_request
        ).exists():
            messages.error(self.request, "You have already rated this shelter for this adoption.")
            return redirect(reverse_lazy('profile details view', kwargs={'pk': self.request.user.pk}))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save the rating and associate it with the shelter and adoption request
        rating = form.save(commit=False)
        rating.shelter = self.shelter
        rating.adopter = self.get_user_profile()
        rating.adoption_request = self.adoption_request
        rating.save()

        messages.success(self.request, "Thank you for your feedback!")

        return redirect(reverse_lazy('shelter page preview', kwargs={'slug': self.shelter.slug}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shelter'] = self.shelter
        return context


class AdoptionRequestsListView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/adoption-requests-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the shelter object
        shelter_pk = self.kwargs.get('pk')
        shelter = get_object_or_404(ShelterProfile, pk=shelter_pk)
        context['shelter'] = shelter

        # Fetch the adoption requests
        context['adopted_or_rejected_requests'] = AdoptionRequest.objects.filter(
            pet__owner=shelter.user, status__in=["Approved", "Rejected"]
        ).order_by('-updated_at')[:5]
        context['pending_requests'] = AdoptionRequest.objects.filter(
            pet__owner=shelter.user, status="Pending"
        ).order_by('-created_at')[:5]

        # Handle the request_id query parameter
        request_id = self.request.GET.get('request_id')  # Extract request_id from the query string
        if request_id:
            try:
                # Get the adoption request detail if request_id is provided
                request_detail = AdoptionRequest.objects.get(pk=request_id, pet__owner=shelter.user)
                context['request_id'] = request_id
                context['request_detail'] = request_detail
            except AdoptionRequest.DoesNotExist:
                # Optionally handle invalid request_id
                context['request_id'] = None
                context['request_detail'] = None

        return context


class UpdateAdoptionRequestStatusView(View):
    def post(self, request, pk, request_pk):
        adoption_request = get_object_or_404(AdoptionRequest, pk=request_pk)
        status = request.POST.get('status')
        if status in ['Approved', 'Rejected']:
            adoption_request.status = status
            adoption_request.pet.status = 'Available' if status == 'Rejected' else 'Adopted'
            adoption_request.pet.save()
            adoption_request.save()
        return redirect('shelter adoption requests', pk=pk)




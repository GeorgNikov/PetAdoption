from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from PetAdoption.accounts.forms import UserLoginForm, UserRegistrationForm
from PetAdoption.accounts.models import ShelterProfile, UserProfile
from PetAdoption.core.forms import ContactForm
from PetAdoption.pets.models import Pet
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

            # Optionally, you could save the contact form data to the database.

            # Display success message
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect back to the contact page

    else:
        form = ContactForm()

        user_profile = UserProfile.objects.get(user=request.user.pk)

        context = {
            'form': form,
            'full_name': user_profile.full_name
        }

    return render(request, 'core/contacts.html', context)


class FAQView(TemplateView):
    template_name = 'core/faq.html'


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
            shelters_with_pet_count.append({
                'shelter': shelter,
                'available_pets_count': available_pets_count,
                'slug': shelter.slug
            })

        # Add the shelter information with the pet count to the context
        context['shelters'] = shelters_with_pet_count

        return context
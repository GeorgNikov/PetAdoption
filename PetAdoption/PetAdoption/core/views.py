from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from PetAdoption.accounts.forms import UserLoginForm, UserRegistrationForm
from PetAdoption.core.forms import ContactForm
from PetAdoption.pets.models import Pet


def index(request):
    form = UserLoginForm(request.POST or None)
    register_form = UserRegistrationForm(request.POST or None)
    pets = Pet.objects.all().order_by('-created_at')[:4] # TODO adopted pets
    # request_user = CustomUser.objects.filter(user=request.user).first()

    if request.user.is_authenticated:
        if request.user.type_user == "Adopter":
            return redirect('profile details view', pk=request.user.pk)
        elif request.user.type_user == "Shelter":
            return redirect('shelter details view', pk=request.user.pk)
        # return redirect('profile details view', pk=request.user.pk)

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

            if user.type_user == "Adopter":
                return redirect('profile details view', pk=user.pk)
            elif user.type_user == "Shelter":
                return redirect('shelter page preview', pk=user.pk)

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

    return render(request, 'core/contacts.html', {'form': form})




class FAQView(TemplateView):
    template_name = 'core/faq.html'
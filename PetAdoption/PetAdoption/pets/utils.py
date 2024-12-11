from django.shortcuts import redirect
from django.contrib import messages

from PetAdoption.accounts.models import UserProfile, ShelterProfile

def check_profile_completion(request, message=None):
    # Check if the user has a completed profile
    user_profile = UserProfile.objects.filter(user=request.user).first()
    shelter_profile = ShelterProfile.objects.filter(user=request.user).first()

    # If the user profile exists but is incomplete
    if user_profile:
        if not user_profile.completed:
            default_message = "Please complete your profile."
            messages.error(request, message or default_message)
            return redirect('profile edit view', pk=user_profile.pk)

    # If the shelter profile exists but is incomplete
    if shelter_profile:
        if not shelter_profile.completed:
            default_message = "Please complete your profile."
            messages.error(request, message or default_message)
            return redirect('shelter edit view', pk=shelter_profile.pk)

    # If neither profile exists
    if not user_profile and not shelter_profile:
        default_message = "Profile does not exist. Please contact support."
        messages.error(request, message or default_message)
        return redirect('index')

    return None  # If everything is fine, return None (meaning no redirection)


# def check_user_type(request):
#     user = request.user
#     if user.type_user == "Adopter":
#         return "Adopter"
#     elif user.type_user == "Shelter":
#         return "Shelter"
#     return None
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect

from PetAdoption.accounts.models import ShelterProfile
from PetAdoption.pets.models import Pet


class ShelterProfileRequiredMixin:
    """
    Mixin to ensure that only users with a ShelterProfile can access the view.
    Redirect unauthenticated users or those without a ShelterProfile to the dashboard or index.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                # Try to fetch the ShelterProfile for the current user
                shelter_profile = ShelterProfile.objects.get(user=request.user)
            except ShelterProfile.DoesNotExist:
                messages.error(request, "You are not authorized to access this page.")
                return redirect('index')  # Redirect to index if user doesn't have ShelterProfile
        else:
            # If the user is not authenticated, show an error and redirect to the login page
            messages.error(request, "You need to log in to access this page.")
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)


class UserAccessMixin(PermissionRequiredMixin):
    """
        Mixin to check if the user has the necessary permissions to access the view.
    """

    group_name = 'Content Moderator'  # Hardcoded group name. BAD DEV.

    def has_group_permission(self):
        """Check if the user belongs to the specified group."""
        try:
            return self.request.user.groups.filter(name=self.group_name).exists()
        except AttributeError:
            # If user does not have the 'groups' attribute or other issues, return False
            return False

    def is_pet_owner(self):
        """Check if the current user is the owner of the pet."""
        pet = get_object_or_404(Pet, slug=self.kwargs.get('pet_slug'))
        return pet.owner == self.request.user

    def has_permission(self):
        """Check if the user has the required permissions (either as a superuser or group owner)."""
        if self.request.user.is_superuser:
            return True

        # Check group permission and pet ownership
        return self.is_pet_owner() or self.has_group_permission()

    def dispatch(self, request, *args, **kwargs):
        """Handle permission checks before proceeding with the view."""
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to access this page.")
            return redirect_to_login(
                next=request.get_full_path(),
                login_url=self.get_login_url(),
                redirect_field_name=self.get_redirect_field_name()
            )

        # Ensure user has required permissions
        if not self.has_permission():
            messages.error(request, "You are not authorized to access this page.")
            return redirect('dashboard')  # Change 'dashboard' to the appropriate page

        # Proceed with the original dispatch
        return super().dispatch(request, *args, **kwargs)
from cloudinary.forms import CloudinaryFileField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import UserProfile, ShelterProfile

UserModel = get_user_model()


class UserEditProfileForm(forms.ModelForm):
    user = forms.HiddenInput()
    slug = forms.HiddenInput()
    image = CloudinaryFileField(required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'province', 'city', 'address', 'image']


class ShelterEditProfileForm(forms.ModelForm):
    class Meta:
        model = ShelterProfile
        fields = [
            "organization_name",
            "phone_number",
            "province",
            "city",
            "address",
            "website",
            "image",
        ]
        widgets = {
            "organization_name": forms.TextInput(
                attrs={
                    "id": "organization_name",
                    "placeholder": "Enter organization name",
                    "class": "",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "id": "phone_number",
                    "placeholder": "Enter phone number",
                    "class": "",
                }
            ),
            "province": forms.Select(
                attrs={"id": "province", "class": "minimal"}
            ),
            "city": forms.Select(
                attrs={"id": "city", "class": "minimal"}
            ),
            "address": forms.TextInput(
                attrs={
                    "id": "address",
                    "placeholder": "Enter address",
                    "class": "",
                }
            ),
            "website": forms.URLInput(
                attrs={
                    "id": "website",
                    "placeholder": "http://website.com",
                    "class": "",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={"id": "image", "class": "custom-file-input"}
            ),
        }


class UserRegistrationForm(UserCreationForm):
    # noinspection PyUnresolvedReferences
    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ('email', 'username', 'password1', 'password2', 'type_user' )



class UserLoginForm(forms.Form):
    class Meta:
        model = UserModel
        fields = ('user', 'password')


# From lector
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password1', 'password2', 'type_user')


# From lector
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = UserModel
        fields = ('email', 'username', 'is_active', 'is_staff', 'groups', 'user_permissions')


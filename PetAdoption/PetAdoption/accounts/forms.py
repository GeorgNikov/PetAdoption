from cloudinary.forms import CloudinaryFileField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy

from .models import UserProfile, CustomUser, ShelterProfile

UserModel = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class UserEditProfileForm(forms.ModelForm):
    user = forms.HiddenInput()
    slug = forms.HiddenInput()
    image = CloudinaryFileField(required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'province', 'city', 'address', 'image']


class ShelterEditProfileForm(forms.ModelForm):
    user = forms.HiddenInput()
    slug = forms.HiddenInput()
    image = CloudinaryFileField(required=False)

    class Meta:
        model = ShelterProfile
        fields = ['organization_name', 'phone_number', 'province', 'city', 'address', 'website', 'image']
        widgets = {
            'website': forms.URLInput(attrs={'placeholder': 'http://website.com'}),
        }



# class UserProfileImageForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['image']


class UserRegistrationForm(UserCreationForm):
    # noinspection PyUnresolvedReferences
    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ('email', 'username', 'password1', 'password2', 'type_user' )
        success_url = reverse_lazy('dashboard')


class UserLoginForm(forms.Form):
    class Meta:
        model = UserModel
        fields = ('user', 'password')



# From lector
class CustomUserCreationForm(UserCreationForm):
    # noinspection PyUnresolvedReferences
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email',)


# From lector
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = "__all__"


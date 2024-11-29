from cloudinary.forms import CloudinaryFileField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy

from .models import UserProfile, CustomUser, ShelterProfile
from .validators import validate_letters_only, validate_organization_name, validate_phone_number

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

    first_name = forms.CharField(
        validators=[
            validate_letters_only,
        ],
        help_text='Enter the first name (letters and spaces only).'
    )

    last_name = forms.CharField(
        validators=[
            validate_letters_only,
        ],
        help_text='Enter the last name (letters and spaces only).'
    )


# class ShelterEditProfileForm(forms.ModelForm):
#     user = forms.HiddenInput()
#     slug = forms.HiddenInput()
#     image = CloudinaryFileField(required=False)
#
#     class Meta:
#         model = ShelterProfile
#         fields = ['organization_name', 'phone_number', 'province', 'city', 'address', 'website', 'image']
#         widgets = {
#             'website': forms.URLInput(attrs={'placeholder': 'http://website.com'}),
#         }
#
#     organization_name = forms.CharField(
#         validators=[
#             validate_organization_name,
#         ],
#         help_text='Can contain letters, numbers and spaces.'
#     )
#
#     phone_number = forms.CharField(
#         validators=[
#             validate_phone_number,
#         ],
#         help_text='Phone number must contain only digits, spaces, parentheses, and dashes.'
#     )
#
#     def clean(self):
#         cleaned_data = super().clean()
#
#         # Clean organization name with the custom validator
#         organization_name = cleaned_data.get('organization_name')
#         if organization_name:
#             validate_organization_name(organization_name)
#
#         # Clean phone number with the custom validator
#         phone_number = cleaned_data.get('phone_number')
#         if phone_number:
#             validate_phone_number(phone_number)
#
#         return cleaned_data


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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Add help text and customize placeholders dynamically
    #     self.fields["organization_name"].help_text = "Can contain letters, numbers, and spaces."



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
    # noinspection PyUnresolvedReferences
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email',)


# From lector
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = "__all__"


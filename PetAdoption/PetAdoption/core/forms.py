from django import forms
from captcha.fields import CaptchaField

from PetAdoption.core.models import ShelterRating


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    captcha = CaptchaField()  # Add CAPTCHA field


class ShelterRatingForm(forms.ModelForm):
    class Meta:
        model = ShelterRating
        fields = ['rating', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 10, 'cols': 46, 'placeholder': 'Write your feedback here...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'feedback': 'Feedback message',
            'rating': 'Rating (1-5)',
        }
        error_messages = {
            'rating': {
                'min_value': 'Rating must be between 10 and 500.',
                'max_value': 'Rating must be between 10 and 500.',
            },
        }
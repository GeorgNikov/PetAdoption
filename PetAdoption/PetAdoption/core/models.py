from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models

from PetAdoption.accounts.models import ShelterProfile

UserModel = get_user_model()

# Create your models here.
class ShelterRating(models.Model):
    RATING_DECIMAL_PLACES = 2
    RATING_MAX_DIGITS = 3
    RATING_DEFAULT_VALUE = 0.00

    FEEDBACK_MIN_LENGTH = 10
    FEEDBACK_MAX_LENGTH = 500

    adopter = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name='adopter',
        null=True
    )

    shelter = models.ForeignKey(
        'accounts.ShelterProfile',
        on_delete=models.CASCADE,
        related_name='shelter',
        null=True
    )

    feedback = models.TextField(
        max_length=FEEDBACK_MAX_LENGTH,
        validators=[
            MinLengthValidator(FEEDBACK_MIN_LENGTH),
            MaxLengthValidator(
                FEEDBACK_MAX_LENGTH,
                message=f'Feedback must be between {FEEDBACK_MIN_LENGTH} and {FEEDBACK_MAX_LENGTH} characters'
            ),
        ]
    )

    rating = models.DecimalField(
        decimal_places=RATING_DECIMAL_PLACES,
        max_digits=RATING_MAX_DIGITS,
        default=RATING_DEFAULT_VALUE,
        null=True,
        blank=True
    )

    adoption_request = models.OneToOneField(
        'pets.AdoptionRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('shelter', 'adopter', 'adoption_request')  # Prevent multiple ratings by the same user for the same shelter


class ContactForm(models.Model):
    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=200
    )

    message = models.TextField()

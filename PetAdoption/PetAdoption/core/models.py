from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from PetAdoption.accounts.models import ShelterProfile

UserModel = get_user_model()

# Create your models here.
class ShelterRating(models.Model):
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

    feedback = models.TextField()

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
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
        unique_together = ('shelter', 'adopter')  # Prevent multiple ratings by the same user for the same shelter


class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

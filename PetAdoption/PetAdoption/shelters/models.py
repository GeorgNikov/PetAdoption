from django.contrib.auth import get_user_model
from django.db import models
from PetAdoption.accounts.models import BaseProfile
from PetAdoption.pets.choices import AdoptionRequestStatusChoices

UserModel = get_user_model()

class ShelterProfile(BaseProfile):
    organization = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=2
    )

    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
    )



class AdoptionRequest(models.Model):
    status = models.CharField(
        max_length=8,
        choices=AdoptionRequestStatusChoices.choices,
        default=AdoptionRequestStatusChoices.PENDING
    )

    from_user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    for_pet = models.ForeignKey(
        'pets.Pet',
        on_delete=models.CASCADE
    )


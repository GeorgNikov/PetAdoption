from django.contrib.auth import get_user_model
from django.db import models
from PetAdoption.pets.choices import PetChoices, PetStatusChoices


UserModel = get_user_model()

class TimeStampBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Pet(TimeStampBaseModel):
    name = models.CharField(
        max_length=100,
        default='No name',
    )

    type = models.CharField(
        max_length=100,
        choices=PetChoices.choices
    )

    bread = models.CharField(
        max_length=100,
        default='Unknown'
    )

    age = models.IntegerField()     # In months

    # description = models.TextField(
    #     blank=True,
    #     null=True,
    # )

    owner = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to='pet_images/',
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=100,
        choices=PetStatusChoices.choices,
        default=PetStatusChoices.AVAILABLE,
    )

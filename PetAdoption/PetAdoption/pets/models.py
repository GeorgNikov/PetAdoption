from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify

from PetAdoption.pets.choices import PetChoices, PetStatusChoices, AdoptionRequestStatusChoices

UserModel = get_user_model()


class TimeStampBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Pet(TimeStampBaseModel):
    NAME_MAX_LENGTH = 30
    TYPE_MAX_LENGTH = 20
    BREED_MAX_LENGTH = 30
    STATUS_MAX_LENGTH = 10
    DESCRIPTION_MAX_LENGTH = 500
    IMG_UPLOAD_TO = 'pet_images/'

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        default='No name',
    )

    # noinspection PyUnresolvedReferences
    type = models.CharField(
        max_length=TYPE_MAX_LENGTH,
        choices=PetChoices.choices
    )

    breed = models.CharField(
        max_length=BREED_MAX_LENGTH,
        default='Unknown'
    )

    age = models.PositiveSmallIntegerField()  # In months

    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to=IMG_UPLOAD_TO,
        blank=True,
        null=True,
    )

    # noinspection PyUnresolvedReferences
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=PetStatusChoices.choices,
        default=PetStatusChoices.AVAILABLE,
    )

    slug = models.SlugField(
        null=True,
        blank=True,
        unique=True,
        editable=False,
    )

    # Add a many-to-many field to track which users have liked the pet
    likes = models.ManyToManyField(
        UserModel,
        related_name='liked_pets',
        blank=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.id}")

        super().save(*args, **kwargs)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.name


class AdoptionRequest(TimeStampBaseModel):
    STATUS_MAX_LENGTH = 8

    # noinspection PyUnresolvedReferences
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=AdoptionRequestStatusChoices.choices,
        default=AdoptionRequestStatusChoices.PENDING
    )

    adopter = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='adoption_requests'
    )

    pet = models.ForeignKey(
        'pets.Pet',
        on_delete=models.CASCADE,
        related_name='adoption_requests'
    )

    message = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.adopter} requests to adopt {self.pet.name}"

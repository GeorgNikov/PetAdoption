from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import slugify

from PetAdoption.pets.choices import PetChoices, PetStatusChoices, AdoptionRequestStatusChoices, PetGenderChoices, \
    PetSizeChoices

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
    GENDER_MAX_LENGTH = 6
    SIZE_MAX_LENGTH = 6
    STATUS_MAX_LENGTH = 10
    DESCRIPTION_MAX_LENGTH = 1500
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

    age = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(240),
        ],
        default=1,
    )  # In months

    # noinspection PyUnresolvedReferences
    gender = models.CharField(
        max_length=GENDER_MAX_LENGTH,
        choices=PetGenderChoices.choices,
        blank=True,
        null=True,
    )

    # noinspection PyUnresolvedReferences
    size = models.CharField(
        max_length=SIZE_MAX_LENGTH,
        choices=PetSizeChoices.choices,
        blank=True,
        null=True,
    )

    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE
    )

    image = CloudinaryField(
        'image',
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
        if not self.slug and self.id:  # Ensure slug is only created after id is assigned
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

from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify

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

    breed = models.CharField(
        max_length=100,
        default='Unknown'
    )

    age = models.IntegerField()     # In months

    description = models.TextField(
        blank=True,
        null=True,
    )

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
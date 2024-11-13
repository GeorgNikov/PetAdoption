from django.db import models


class AdoptionRequestStatusChoices(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'


class PetChoices(models.TextChoices):
    DOG = 'Dog', 'Dog'
    CAT = 'Cat', 'Cat'
    BIRD = 'Bird', 'Bird'
    REPTILE = 'Reptile', 'Reptile'
    FISH = 'Fish', 'Fish'
    OTHER = 'Other', 'Other'


class PetStatusChoices(models.TextChoices):
    AVAILABLE = 'Available', 'Available'
    ADOPTED = 'Adopted', 'Adopted'
    PENDING = 'Pending', 'Pending'

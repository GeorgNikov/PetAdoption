from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class AdoptionFeedBack(models.Model):
    from_user = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name='from_user',
        null=True
    )

    to_shelter = models.ForeignKey(
        'accounts.ShelterProfile',
        on_delete=models.CASCADE,
        related_name='to_shelter',
        null=True
    )

    for_pet = models.ForeignKey(
        'pets.Pet',
        on_delete=models.CASCADE,
        related_name='for_pet',
        null=True
    )

    review = models.TextField()

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
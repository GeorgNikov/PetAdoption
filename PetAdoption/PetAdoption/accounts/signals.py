from django.db.models.signals import post_save
from django.dispatch import receiver

from PetAdoption.accounts.models import UserProfile, ShelterProfile, CustomUser
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Creating profile for user {instance.pk} of type {instance.type_user}")
        if instance.type_user == "Adopter" and not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)
        elif instance.type_user == "Shelter" and not ShelterProfile.objects.filter(user=instance).exists():
            ShelterProfile.objects.create(user=instance)
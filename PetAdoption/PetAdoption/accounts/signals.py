from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from PetAdoption.accounts.models import UserProfile, ShelterProfile


#Create profile after registration
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.type_user == "Adopter":
            UserProfile.objects.create(
                user=instance
            )
        elif instance.type_user == "Shelter":
            ShelterProfile.objects.create(
                user=instance
            )

from cloudinary.uploader import destroy
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from PetAdoption.accounts.models import UserProfile, ShelterProfile, CustomUser



# Create a profile when a user is created
@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.type_user == "Adopter" and not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)
        elif instance.type_user == "Shelter" and not ShelterProfile.objects.filter(user=instance).exists():
            ShelterProfile.objects.create(user=instance)




# Delete the Cloudinary image when the profile is deleted
@receiver(post_delete, sender=UserProfile)
def delete_cloudinary_image(sender, instance, **kwargs):
    # Check if the profile has an image
    if instance.image:
        # Extract the public_id from the image URL
        public_id = instance.image.public_id

        # Delete the image from Cloudinary
        destroy(public_id)

        # Delete the image from the database
        # instance.image.delete()
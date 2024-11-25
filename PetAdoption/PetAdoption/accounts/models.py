from cloudinary.models import CloudinaryField
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify

from PetAdoption.accounts.choices import UserTypeChoices, BulgarianProvinces
from PetAdoption.accounts.managers import AppUserManager
from PetAdoption.accounts.utils import load_bulgarian_cities


# Extended AbstractBaseUser model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_MAX_LENGTH = 7

    USERNAME_MAX_LENGTH = 50
    USERNAME_MIN_LENGTH = 3

    type_user = models.CharField(
        max_length=USER_TYPE_MAX_LENGTH,
        choices=UserTypeChoices,
        default=UserTypeChoices.ADOPTER,
    )

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            MinLengthValidator(USERNAME_MIN_LENGTH),
            AbstractUser.username_validator
        ],
        unique=True,
    )

    email = models.EmailField(
        unique=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
        editable=True,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = AppUserManager()


class BaseProfile(models.Model):
    PHONE_NUMBER_MAX_LENGTH = 13

    ADDRESS_MAX_LENGTH = 100
    CITY_MAX_LENGTH = 60
    PROVINCE_MAX_LENGTH = 60

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH,
        null=True,
        blank=True,
    )

    address = models.CharField(
        max_length=ADDRESS_MAX_LENGTH
    )

    city = models.CharField(
        max_length=CITY_MAX_LENGTH,
        choices=load_bulgarian_cities(),
        default=load_bulgarian_cities()[0],
    )

    province = models.CharField(
        max_length=PROVINCE_MAX_LENGTH,
        choices=BulgarianProvinces,
        default=BulgarianProvinces.SOFIA_CITY,
    )

    completed = models.BooleanField(
        default=False,
        blank=True,
    )

    image = CloudinaryField(
        'image',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
    )

    @property
    def full_address(self):
        return f'{self.province}, {self.city}, {self.address}'

    class Meta:
        abstract = True


class UserProfile(BaseProfile):
    FIRST_NAME_MAX_LENGTH = 30
    FIRST_NAME_MIN_LENGTH = 3

    LAST_NAME_MAX_LENGTH = 30
    LAST_NAME_MIN_LENGTH = 3

    IMG_UPLOAD_TO = 'user_profile_images/'  # Cloudinary

    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        validators=[
            MinLengthValidator(FIRST_NAME_MIN_LENGTH)
        ],
    )

    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        validators=[
            MinLengthValidator(LAST_NAME_MIN_LENGTH)
        ],
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True,
        editable=True,
    )

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='user_profile',
    )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if not self.slug:  # Ensure slug is only generated if it doesn't already exist
            base_slug = slugify(self.full_name or f"user-{self.user.pk}")
            slug = base_slug
            counter = 1
            while UserProfile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name or self.user.username}"


class ShelterProfile(BaseProfile):
    ORGANIZATION_NAME_MAX_LENGTH = 100
    ORGANIZATION_NAME_MIN_LENGTH = 3

    WEBSITE_MAX_LENGTH = 100
    IMG_UPLOAD_TO = 'shelter_profile_images/'  # Cloudinary

    organization_name = models.CharField(
        max_length=ORGANIZATION_NAME_MAX_LENGTH,
        unique=True,
        validators=[
            MinLengthValidator(ORGANIZATION_NAME_MIN_LENGTH)
        ],
        null=True,
        blank=True,
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True,
        editable=True,
    )

    website = models.URLField(
        max_length=WEBSITE_MAX_LENGTH,
        blank=True,
        null=True,
    )

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='shelter_profile',
    )

    def save(self, *args, **kwargs):
        # Generate the slug when organization_name is set
        if self.organization_name:
            base_slug = slugify(self.organization_name)
        else:
            base_slug = slugify(f"user-{self.user.pk}")

        slug = base_slug
        # Ensure we don't try to generate the slug if it's already set or during object creation
        if not self.pk:  # Only when the object is being created
            slug = f"{base_slug}-{self.pk}"  # Using the pk to create a unique slug
        else:
            # If the organization_name has changed, update the slug
            if self.pk and self.slug != f"{base_slug}-{self.pk}":
                slug = f"{base_slug}-{self.pk}"

        # Ensure the final slug is unique
        counter = 1
        original_slug = slug
        while ShelterProfile.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        self.slug = slug

        # Call the parent save method
        super().save(*args, **kwargs)

    def __str__(self):
        return self.organization_name if self.organization_name else f"User-{self.user.pk}"

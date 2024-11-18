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
    )

    USERNAME_FIELD = 'username'

    objects = AppUserManager()



class BaseProfile(models.Model):
    PHONE_NUMBER_MAX_LENGTH = 13

    ADDRESS_MAX_LENGTH = 100

    CITY_MAX_LENGTH = 60
    PROVINCE_MAX_LENGTH = 60

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH,
        unique=True,
        null=True,
        blank=True,
    )

    address = models.CharField(
        max_length=ADDRESS_MAX_LENGTH
    )

    city = models.CharField(
        max_length=CITY_MAX_LENGTH,
        choices=load_bulgarian_cities(),
        default='Sofia',
    )

    province = models.CharField(
        max_length=PROVINCE_MAX_LENGTH,
        choices=BulgarianProvinces,
        default='Sofia Province',
    )

    slug = models.SlugField(
        blank=True,
        null=True,
        editable=True,
    )

    completed = models.BooleanField(
        default=False,
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

    image = models.ImageField(
        upload_to=IMG_UPLOAD_TO,
        blank=True,
        null=True,
    )

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE
    )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.slug:
            if self.full_name:
                self.slug = slugify(f"{self.full_name}-{self.pk}")
            else:
                self.slug = slugify(f"{self.user.username}-{self.pk}")

        super().save(*args, **kwargs)


class ShelterProfile(BaseProfile):
    ORGANIZATION_NAME_MAX_LENGTH = 100
    ORGANIZATION_NAME_MIN_LENGTH = 3

    RATING_MAX_DIGITS = 2
    RATING_DECIMAL_PLACES = 2

    IMG_UPLOAD_TO = 'shelter_profile_images/'    # Cloudinary

    organization_name = models.CharField(
        max_length=ORGANIZATION_NAME_MAX_LENGTH,
        unique=True,
        validators=[
            MinLengthValidator(ORGANIZATION_NAME_MIN_LENGTH)
        ],
        null=True,
        blank=True,
    )

    rating = models.DecimalField(
        max_digits=RATING_MAX_DIGITS,
        decimal_places=RATING_DECIMAL_PLACES,
        null=True,
        blank=True
    )

    image = models.ImageField(
        upload_to=IMG_UPLOAD_TO,
        blank=True,
        null=True,
    )

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.slug:
            if self.organization_name:
                self.slug = slugify(f"{self.organization_name}-{self.pk}")
            else:
                self.slug = slugify(f"{self.user.username}-{self.pk}")

        super().save(*args, **kwargs)


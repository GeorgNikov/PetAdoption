from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

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
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.ADOPTER,
    )

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            MinLengthValidator(USERNAME_MIN_LENGTH),
            AbstractUser.username_validator
        ],
        unique=True,
        help_text=_(
            "Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
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
    LAST_NAME_MAX_LENGTH = 30

    PHONE_NUMBER_MAX_LENGTH = 13

    BIO_MAX_LENGTH = 500

    ADDRESS_MAX_LENGTH = 100

    CITY_MAX_LENGTH = 60
    PROVINCE_MAX_LENGTH = 60

    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
    )

    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
    )

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH,
        unique=True,
        null=True,
        blank=True,
    )

    # bio = models.TextField(
    #     max_length=BIO_MAX_LENGTH,
    #     blank=True,
    #     null=True,
    # )

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
        choices=BulgarianProvinces.choices,
        default='Sofia Province',
    )

    image = models.ImageField(
        upload_to='user_profile_images/',  # Cloudinary
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

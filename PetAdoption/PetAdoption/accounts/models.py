from cloudinary.models import CloudinaryField
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify

from PetAdoption.accounts.choices import UserTypeChoices, BulgarianProvinces
from PetAdoption.accounts.managers import AppUserManager
from PetAdoption.accounts.utils import load_bulgarian_cities
from PetAdoption.accounts.validators import validate_organization_name, \
    validate_letters_only, validate_phone_number, validate_type_user


# Extended AbstractBaseUser model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_MAX_LENGTH = 7

    USERNAME_MAX_LENGTH = 50
    USERNAME_MIN_LENGTH = 3

    type_user = models.CharField(
        max_length=USER_TYPE_MAX_LENGTH,
        choices=UserTypeChoices,
        default=UserTypeChoices.ADOPTER,
        validators=[
            validate_type_user,
        ],
        error_messages={
            'invalid': "Invalid user type. Please select 'Adopter' or 'Shelter'."
        },
    )

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            MinLengthValidator(USERNAME_MIN_LENGTH),
            AbstractUser.username_validator
        ],
        error_messages={
            'username': [
                'This field may contain only letters, digits and @/./+/-/_ characters.'
            ],
            'unique': 'A user with that username already exists.'
        },
        unique=True,
    )

    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with that email already exists.'
        },
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
        validators=[
            validate_phone_number,
        ],
        help_text='Phone number must contain only digits, spaces, parentheses, and dashes.'
    )

    address = models.CharField(
        max_length=ADDRESS_MAX_LENGTH
    )

    city = models.CharField(
        max_length=CITY_MAX_LENGTH,
        choices=load_bulgarian_cities(),
        default=load_bulgarian_cities()[0][1],
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
    FIRST_NAME_MIN_LENGTH = 2

    LAST_NAME_MAX_LENGTH = 30
    LAST_NAME_MIN_LENGTH = 2

    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        validators=[
            MinLengthValidator(FIRST_NAME_MIN_LENGTH,
                               message=f"The first name must be at least {FIRST_NAME_MIN_LENGTH} characters long."),
            validate_letters_only,
        ],
        help_text=f'Must contain only letters and be between {LAST_NAME_MIN_LENGTH} and {LAST_NAME_MAX_LENGTH} characters long.',
        error_messages={
            'invalid': 'The first name can only contain letters.',
            'max_length': f'The first name must not exceed {FIRST_NAME_MAX_LENGTH} characters.',
            'min_length': f'The first name must be at least {FIRST_NAME_MIN_LENGTH} characters long.'
        }
    )

    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        validators=[
            MinLengthValidator(LAST_NAME_MIN_LENGTH,
                               message=f"The last name must be at least {LAST_NAME_MIN_LENGTH} characters long."),
            validate_letters_only,
        ],
        help_text=f'Must contain only letters and be between {LAST_NAME_MIN_LENGTH} and {LAST_NAME_MAX_LENGTH} characters long.',
        error_messages={
            'invalid': 'The last name can only contain letters.',
            'max_length': f'The last name must not exceed {LAST_NAME_MAX_LENGTH} characters.',
            'min_length': f'The last name must be at least {LAST_NAME_MIN_LENGTH} characters long.'
        }
    )

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='user_profile',
    )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name if self.full_name is not None else f"{self.user.username}"



class ShelterProfile(BaseProfile):
    ORGANIZATION_NAME_MAX_LENGTH = 100
    ORGANIZATION_NAME_MIN_LENGTH = 3

    WEBSITE_MAX_LENGTH = 100
    IMG_UPLOAD_TO = 'shelter_profile_images/'  # Cloudinary

    organization_name = models.CharField(
        max_length=ORGANIZATION_NAME_MAX_LENGTH,
        unique=True,
        validators=[
            MinLengthValidator(ORGANIZATION_NAME_MIN_LENGTH),
            validate_organization_name,
        ],
        null=True,
        blank=True,
        help_text='Can contain letters, numbers and spaces.'
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True,
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
        if not self.slug:
            self.slug = slugify(f"shelter-{self.user.username}-{self.user.pk}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.organization_name if self.organization_name else f"{self.user.username}"

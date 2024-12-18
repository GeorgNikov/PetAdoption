# Generated by Django 5.1.3 on 2024-11-29 20:38

import PetAdoption.accounts.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_shelterprofile_city_alter_userprofile_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shelterprofile',
            name='organization_name',
            field=models.CharField(blank=True, help_text='Can contain letters, numbers and spaces.', max_length=100, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(3), PetAdoption.accounts.validators.validate_organization_name]),
        ),
        migrations.AlterField(
            model_name='shelterprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=13, null=True, validators=[PetAdoption.accounts.validators.validate_phone_number]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(3), PetAdoption.accounts.validators.validate_letters_only]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(3), PetAdoption.accounts.validators.validate_letters_only]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=13, null=True, validators=[PetAdoption.accounts.validators.validate_phone_number]),
        ),
    ]

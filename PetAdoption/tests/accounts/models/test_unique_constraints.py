from django.db.utils import IntegrityError
from django.test import TestCase

from PetAdoption.accounts.models import CustomUser


class CustomUserUniqueFieldsTest(TestCase):
    def test_unique_email(self):
        # Test email uniqueness
        user1 = CustomUser.objects.create_user(
            username='user1',
            email='testuser@example.com',
            password='password123',
            type_user='ADOPTER'
        )

        with self.assertRaises(IntegrityError):
            user2 = CustomUser.objects.create_user(
                username='user2',
                email='testuser@example.com',  # Same email
                password='password123',
                type_user='SHELTER'
            )

    def test__unique_username(self):
        # Test username uniqueness
        user1 = CustomUser.objects.create_user(
            username='testuser1',
            email='user1@example.com',
            password='password123',
            type_user='ADOPTER'
        )

        with self.assertRaises(IntegrityError):
            user2 = CustomUser.objects.create_user(
                username='testuser1',  # Same username
                email='user2@example.com',
                password='password123',
                type_user='SHELTER'
            )

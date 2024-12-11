from django.test import TestCase
from django.contrib.auth import get_user_model
from PetAdoption.accounts.models import UserProfile, ShelterProfile
from django.utils.text import slugify


class TestUserProfileIntegrationTest(TestCase):

    def setUp(self):
        self.adopter_user = get_user_model().objects.create_user(
            username="adopteruser",
            email="adopter@example.com",
            password="testpassword123",
            type_user="Adopter",
        )

        self.shelter_user = get_user_model().objects.create_user(
            username="shelteruser1",
            email="shelter@example.com",
            password="testpassword123",
            type_user="Shelter",
        )

    def test__create_user_and_profile_integration(self):
        # Test Adopter Profile Creation
        user_profile = UserProfile.objects.get(user=self.adopter_user)
        self.assertEqual(user_profile.user, self.adopter_user)
        self.assertEqual(user_profile.first_name, '')
        self.assertEqual(user_profile.last_name, '')

        # Test Shelter Profile Creation
        shelter_profile = ShelterProfile.objects.get(user=self.shelter_user)
        self.assertEqual(shelter_profile.user, self.shelter_user)
        self.assertEqual(shelter_profile.slug, slugify(f"shelter-{self.shelter_user.username}-{self.shelter_user.pk}"))


    def test__user_type_and_profile_association(self):
        self.assertTrue(self.shelter_user.shelter_profile)
        self.assertEqual(self.shelter_user.shelter_profile.user, self.shelter_user)
        self.assertEqual(self.shelter_user.shelter_profile.organization_name, None)

    def test__user_profile_creation_with_fields__result_empty_fields(self):
        self.adopter_user.first_name = 'John'
        self.adopter_user.last_name = 'Doe'
        self.adopter_user.save()  # Save user with these fields

        self.user_profile = UserProfile.objects.get(user=self.adopter_user)

        # Signal create profile and expected ''
        self.assertEqual(self.user_profile.first_name, '')
        self.assertEqual(self.user_profile.last_name, '')


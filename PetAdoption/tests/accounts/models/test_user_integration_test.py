from django.test import TestCase
from django.contrib.auth import get_user_model
from PetAdoption.accounts.models import UserProfile, ShelterProfile
from PetAdoption.accounts.choices import UserTypeChoices
from django.utils.text import slugify


class TestCustomUserIntegrationTest(TestCase):

    def setUp(self):
        self.adopter_user = get_user_model().objects.create_user(
            username='adopteruser1',
            email='adopter@example.com',
            password='testpassword123',
            type_user=UserTypeChoices.ADOPTER
        )

        self.adopter_user_2 = get_user_model().objects.create_user(
            username='adopteruser2',
            email='adopter2@example.com',
            password='testpassword123',
            type_user=UserTypeChoices.ADOPTER
        )

        self.shelter_user = get_user_model().objects.create_user(
            username='shelteruser1',
            email='shelter@example.com',
            password='testpassword123',
            type_user=UserTypeChoices.SHELTER
        )

        self.shelter_user_2 = get_user_model().objects.create_user(
            username='shelteruser2',
            email='shelter2@example.com',
            password='testpassword123',
            type_user=UserTypeChoices.SHELTER
        )

    def test__create_adopter_user(self):
        user_profile = UserProfile.objects.get(user=self.adopter_user)
        self.assertEqual(user_profile.user, self.adopter_user)

    def test__create_shelter_user(self):
        shelter_profile = ShelterProfile.objects.get(user=self.shelter_user)

        self.assertEqual(shelter_profile.user, self.shelter_user)

        expected_slug = f"{slugify(self.shelter_user.username)}-{self.shelter_user.pk}"
        self.assertEqual(shelter_profile.slug, expected_slug)

    def test__user_type_validation(self):
        user = get_user_model().objects.create_user(
            username='validuser',
            email='valid@example.com',
            password='testpassword123',
            type_user='Adopter'
        )
        self.assertEqual(user.type_user, 'Adopter')


    def test__shelter_profile_slug_unique_for_shelter(self):
        profile1 = ShelterProfile.objects.get(user=self.shelter_user)
        profile2 = ShelterProfile.objects.get(user=self.shelter_user_2)

        self.assertNotEqual(profile1.slug, profile2.slug)

    def test__shelter_profile_slug_based_on_username_and_pk(self):
        shelter_profile = ShelterProfile.objects.get(user=self.shelter_user)
        expected_slug = f"{slugify(self.shelter_user.username)}-{self.shelter_user.pk}"
        self.assertEqual(shelter_profile.slug, expected_slug)

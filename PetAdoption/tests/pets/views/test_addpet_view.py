from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from PetAdoption.accounts.models import ShelterProfile

UserModel = get_user_model()


class AddPetViewTestCase(TestCase):

    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            type_user='shelter',
        )
        self.user_with_shelter = UserModel.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='password123',
            type_user='shelter',
        )
        self.user_without_shelter = UserModel.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123',
            type_user='adopter',
        )

        self.shelter_profile = ShelterProfile.objects.create(user=self.user)
        self.url = reverse('dashboard')


    def test__add_pet_with_shelter_profile(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test__access_for_user_with_shelter_profile(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test__access_for_user_without_shelter_profile(self):
        self.client.login(username='testuser2', password='password123')

        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('dashboard'))
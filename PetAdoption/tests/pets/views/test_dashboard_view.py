from django.db import connection
from django.test import TestCase
from django.urls import reverse
from django.core.paginator import Page
from django.contrib.auth import get_user_model

from PetAdoption.pets.models import Pet

User = get_user_model()


class DashboardViewTest(TestCase):
    def setUp(self):
        # Create a user and log them in
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Create some sample pets
        self.pets = [
            Pet.objects.create(
                name=f"Pet {i}",
                age=i,
                type="Dog",
                gender="Male",
                breed="Labrador",
                size="Medium",
                status="Available" if i % 2 == 0 else "Pending",
                owner=self.user
            )
            for i in range(10)
        ]

        # Create a pet liked by the user
        self.liked_pet = Pet.objects.create(
            name="Liked Pet",
            age=5,
            type="Cat",
            gender="Female",
            size="Small",
            status="Available",
            owner=self.user
        )
        self.liked_pet.likes.add(self.user)

        self.url = reverse('dashboard')  # Replace with the actual name of your dashboard URL pattern

    def test__dashboard_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pets/dashboard.html')

    def test__dashboard_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Ensure the context contains paginated pets
        pets = response.context['pets']
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(len(pets), 6)  # Default paginate_by is 6

    def test__dashboard_filters_by_status(self):
        response = self.client.get(self.url)
        pets = response.context['pets']
        self.assertTrue(all(pet.status in ["Available", "Pending"] for pet in pets))

    def test__dashboard_shows_liked_status(self):
        response = self.client.get(self.url)
        pets = response.context['pets']
        liked_pet = next((pet for pet in pets if pet.name == "Liked Pet"), None)
        self.assertIsNotNone(liked_pet)
        self.assertTrue(liked_pet.liked)

    def test__dashboard_applies_age_filter(self):
        response = self.client.get(self.url, {'age': '0-12'})
        pets = response.context['pets']
        self.assertTrue(all(0 <= pet.age < 12 for pet in pets))

    def test__dashboard_applies_type_filter(self):
        response = self.client.get(self.url, {'type': 'Dog'})
        pets = response.context['pets']
        self.assertTrue(all(pet.type.lower() == 'dog' for pet in pets))

    def test__dashboard_applies_gender_filter(self):
        response = self.client.get(self.url, {'gender': 'Male'})
        pets = response.context['pets']
        self.assertTrue(all(pet.gender.lower() == 'male' for pet in pets))

    def test__dashboard_applies_size_filter(self):
        response = self.client.get(self.url, {'size': 'Medium'})
        pets = response.context['pets']
        self.assertTrue(all(pet.size.lower() == 'medium' for pet in pets))

    def test__dashboard_handles_multiple_filters(self):
        response = self.client.get(self.url, {'type': 'Dog', 'gender': 'Male', 'age': '0-12'})
        pets = response.context['pets']
        self.assertTrue(
            all(
                pet.type.lower() == 'dog'
                and pet.gender.lower() == 'male'
                and 0 <= pet.age < 12
                for pet in pets
            )
        )

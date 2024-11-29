from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, RequestFactory
from django.urls import reverse, reverse_lazy

from PetAdoption.pets.models import Pet

UserModel = get_user_model()


def reset_sequence(app_label, model_name):
    with connection.cursor() as cursor:
        table_name = f'{app_label}_{model_name}'
        cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), 1, false)")


class IndexViewTest(TestCase):

    def setUp(self):
        self.user = UserModel.objects.create_user(username="testuser", password="password123")
        self.pet1 = Pet.objects.create(name="Fido", status="Adopted", owner=self.user)
        self.pet2 = Pet.objects.create(name="Bella", status="Adopted", owner=self.user)

        self.url = reverse('index')
        self.form_data = {'username': 'testuser', 'password': 'password123'}
        self.invalid_form_data = {'username': 'wronguser', 'password': 'wrongpassword'}
        self.registration_data = {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com',
            'type_user': 'adopter',  # Assuming the user is an adopter
        }

    def test_authenticated_user_redirected_to_dashboard(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)

        # Check that the user was redirected to the dashboard
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_with_valid_credentials_redirects_to_dashboard(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.url, self.form_data)

        # Check that the user was redirected to the dashboard
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_with_invalid_credentials_shows_error(self):
        response = self.client.post(self.url, self.invalid_form_data)

        # Check that the error message is displayed
        self.assertContains(response, "Invalid username or password.")

    def test_no_pets_in_database_shows_empty_list(self):
        Pet.objects.all().delete()  # Remove all pets
        response = self.client.get(self.url)
        self.assertEqual(response.context['pets'], [])

    def test_pets_are_displayed_correctly(self):
        response = self.client.get(self.url)
        self.assertIn(self.pet1, response.context['pets'])

    def test_pets_are_displayed_on_index(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Fido")
        self.assertContains(response, "Bella")

    def test_correct_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_context_data(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        self.assertIn('register_form', response.context)
        self.assertIn('pets', response.context)
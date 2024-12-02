from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

UserModel = get_user_model()

class IndexRedirectTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username='testuser', password='password123')

    def test__redirect_authenticated_user_to_dashboard(self):
        self.client.login(username='testuser', password='password123')

        response = self.client.get(reverse('index'))

        self.assertRedirects(response, reverse('dashboard'))

    def test__index_page_for_anonymous_user(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)

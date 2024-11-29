from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class ProfileDeleteViewTest(TestCase):
    def setUp(self):
        # Create two test users
        self.user1 = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password1',
            type_user='adopter'
        )
        self.user2 = get_user_model().objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password2',
            type_user='shelter'
        )

        # URL for the delete view for user1
        self.delete_url = reverse('profile delete', kwargs={'pk': self.user1.pk})

    def test_delete_profile_authorized(self):

        self.client.login(username='user1', password='password1')
        response = self.client.post(self.delete_url)

        # Check if the user is deactivated
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)

        # Check for success message and redirection
        self.assertRedirects(response, reverse('index'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your profile has been DELETED successfully.")

    def test_delete_profile_unauthorized(self):

        self.client.login(username='user2', password='password2')
        response = self.client.post(self.delete_url)

        # Ensure user1 is still active
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_active)

        # Check for forbidden response
        self.assertEqual(response.status_code, 403)

    def test_delete_profile_not_logged_in(self):

        response = self.client.post(self.delete_url)

        # Ensure user1 is still active
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_active)

        # Check if redirected to login page
        self.assertRedirects(response, f"{reverse('login')}?next={self.delete_url}")

    def test_delete_nonexistent_profile(self):

        self.client.login(username='user1', password='password1')
        non_existent_url = reverse('profile delete', kwargs={'pk': 9999})
        response = self.client.post(non_existent_url, follow=True)

        # Check if user1 is still active
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_active)

        # Check for error message and redirection
        self.assertRedirects(response, reverse('dashboard'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Profile not found.")

    def test_get_profile_delete_page(self):

        self.client.login(username='user1', password='password1')
        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/userprofile-confirm-delete.html')

    def test_get_profile_delete_page_unauthorized(self):

        self.client.login(username='user2', password='password2')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ClinicProfile

User = get_user_model()


class ClinicAuthenticationTests(TestCase):
    def create_user(self, user, password, role=None):
        user = User.objects.create_user(username=username, password=password)
        if role:
            ClinicProfile.objects.create(user=user, role=role)
        return user

    def test_anonymous_user_cannot_access_receptionist_dashboard(self):
        response = self.client.get(reverse('receptionist_dashboard'))
        self.assertEqual(response.status_code, 301)
        self.assertIn('/login/', response.url)

    def test_anonymous_user_cannot_access_doctor_dashboard(self):
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 301)
        self.assertIn('/login/', response.url)

    def test_receptionist_can_log_in_successfully(self):
        self.create_user('receptionist', 'StrongPass1!', ClinicProfile.RECEPTIONIST)

        response = self.client.post(reverse('login'), {'username': 'receptionist', 'password': 'StrongPass1!'} )

        self.assertRedirects(response, reverse('receptionist_dashboard'))

    def test_doctor_can_log_in_successfully(self):
        self.create_user('doctor', 'StrongPass1!', ClinicProfile.DOCTOR)

        response = self.client.post(reverse('login'), {'username': 'doctor', 'password': 'StrongPass1!'})

        self.assertRedirects(response, reverse('doctor_dashboard'))

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post(reverse('login'), {'username': 'missing', 'password': 'wrong'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')

    def test_user_without_role_cannot_access_dashboard(self):
        user = self.create_user('no_role', 'StrongPass1!')
        self.client.force_login(user)

        response = self.client.get(reverse('receptionist_dashboard'))
        self.assertEqual(response.status_code, 301)
        self.assertIn('/login/', response.url)

    def test_user_with_missing_role_profile_is_handled_safely(self):
        user = User.objects.create_user(username='missing_profile', password='StrongPass1!')
        response = self.client.post(reverse('login'), {'username': 'missing_profile', 'password': 'StrongPass1!'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'approved clinic role')

    def test_receptionist_cannot_view_doctor_dashboard(self):
        user = self.create_user('receptionist_only', 'StrongPass1!', ClinicProfile.RECEPTIONIST)
        self.client.force_login(user)

        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 301)
        self.assertIn('/login/', response.url)

    def test_doctor_cannot_view_receptionist_dashboard(self):
        user = self.create_user('doctor_only', 'StrongPass1!', ClinicProfile.DOCTOR)
        self.client.force_login(user)

        response = self.client.get(reverse('receptionist_dashboard'))
        self.assertEqual(response.status_code, 301)
        self.assertIn('/login/', response.url)

    def test_logout_works_for_post_and_clears_session(self):
        user = self.create_user('logout_user', 'StrongPass1!', ClinicProfile.RECEPTIONIST)
        self.client.force_login(user)

        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_get_logout_is_rejected(self):
        user = self.create_user('logout_get', 'StrongPass1!', ClinicProfile.DOCTOR)
        self.client.force_login(user)

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 405)

    def test_dashboard_empty_states_are_visible(self):
        user = self.create_user('empty_dashboard', 'StrongPass1!', ClinicProfile.RECEPTIONIST)
        self.client.force_login(user)

        response = self.client.get(reverse('receptionist_dashboard'))
        self.assertContains(response, 'No patients have been registered today.')
        self.assertContains(response, 'The patient queue will appear once the relevant module is integrated.')

    def test_doctor_empty_queue_message_is_visible(self):
        user = self.create_user('doctor_empty', 'StrongPass1!', ClinicProfile.DOCTOR)
        self.client.force_login(user)

        response = self.client.get(reverse('doctor_dashboard'))
        self.assertContains(response, 'No patients are currently assigned to your queue.')

    def test_restricted_url_access_does_not_bypass_role_checks(self):
        user = self.create_user('restricted', 'StrongPass1!', ClinicProfile.DOCTOR)
        self.client.force_login(user)

        response = self.client.get('/receptionist-dashboard/')

        self.assertEqual(response.status_code, 301)
        self.assertIn('/login/', response.url)

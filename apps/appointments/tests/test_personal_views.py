from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User

class PersonalAppointmentsViewsTests(TestCase):
    def setUp(self):
        # Create a patient user
        self.patient = User.objects.create_user(
            username='patient1',
            email='patient1@example.com',
            password='testpass123',
            role='patient'
        )
        # Create a provider user
        self.provider = User.objects.create_user(
            username='provider1',
            email='provider1@example.com',
            password='testpass123',
            role='provider'
        )
        self.client = Client()

    def test_provider_directory_requires_login(self):
        url = reverse('appointments:provider_directory')
        response = self.client.get(url)
        # should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_provider_directory_authenticated(self):
        self.client.login(username='patient1', password='testpass123')
        url = reverse('appointments:provider_directory')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find a Provider')

    def test_provider_detail_view(self):
        self.client.login(username='patient1', password='testpass123')
        url = reverse('appointments:provider_detail', args=[self.provider.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # provider may not have first/last name set in the test user; assert username is present
        self.assertContains(response, self.provider.username)

    def test_book_personal_get(self):
        self.client.login(username='patient1', password='testpass123')
        url = reverse('appointments:book_personal_appointment', args=[self.provider.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book Personal Appointment')

    def test_my_personal_appointments_requires_login(self):
        url = reverse('appointments:my_personal_appointments')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_my_personal_appointments_authenticated(self):
        self.client.login(username='patient1', password='testpass123')
        url = reverse('appointments:my_personal_appointments')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'My Personal Appointments')

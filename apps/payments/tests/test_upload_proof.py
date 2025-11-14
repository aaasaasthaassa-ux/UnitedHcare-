from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.payments.models import Payment


class UploadProofTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client = Client()
        self.client.force_login(self.user)

    def test_upload_sets_pending(self):
        # Create an unpaid payment for the logged-in user
        payment = Payment.objects.create(patient=self.user, amount='250.00', payment_status='unpaid')

        url = reverse('payments:upload_proof', args=[payment.id])

        # Create a small dummy image file
        img = SimpleUploadedFile('proof.jpg', b'JPEGIMAGEBYTES', content_type='image/jpeg')

        resp = self.client.post(url, {'transaction_id': 'TRX-12345', 'payment_proof': img}, follow=True)

        # Reload from DB and assert status changed to pending and method set to online
        payment.refresh_from_db()
        self.assertEqual(payment.payment_status, 'pending')
        self.assertEqual(payment.payment_method, 'online')
        self.assertEqual(payment.transaction_id, 'TRX-12345')
        # Either the uploaded file was saved or a URL was set
        self.assertTrue(bool(payment.payment_proof_file) or bool(payment.payment_proof_url))

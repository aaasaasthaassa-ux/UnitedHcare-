from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_welcome_email(user_email, user_name):
    subject = 'Welcome to UH Care'
    message = f'Hello {user_name},\n\nWelcome to UH Care. We will notify you about your appointments.'
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@uhcare.local'
    send_mail(subject, message, from_email, [user_email], fail_silently=True)

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from .models import Notification, EmailLog, SMSLog, NotificationPreference
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Centralized service for sending notifications
    """
    
    @staticmethod
    def send_notification(user, notification_type, title, message, 
                         related_object=None, action_url='', action_text='View Details',
                         send_email=True, send_sms=False):
        """
        Send notification through multiple channels
        """
        # Get user preferences
        try:
            prefs = user.notification_preferences
        except NotificationPreference.DoesNotExist:
            prefs = NotificationPreference.objects.create(user=user)
        
        # Create in-app notification
        if prefs.enable_in_app:
            notification = Notification.create_notification(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_object=related_object,
                action_url=action_url,
                action_text=action_text
            )
        
        # Send email
        if send_email and prefs.enable_email:
            NotificationService.send_email_notification(
                user, notification_type, title, message, action_url
            )
        
        # Send SMS
        if send_sms and prefs.enable_sms:
            NotificationService.send_sms_notification(
                user, notification_type, message
            )
    
    @staticmethod
    def send_email_notification(user, email_type, subject, message, action_url=''):
        """
        Send email notification
        """
        try:
            # Create email log
            email_log = EmailLog.objects.create(
                recipient=user,
                subject=subject,
                message=message,
                email_type=email_type,
            )
            
            # Render email template
            html_message = render_to_string('notifications/email_template.html', {
                'user': user,
                'title': subject,
                'message': message,
                'action_url': action_url,
                'site_name': 'UH Care',
            })
            plain_message = strip_tags(html_message)
            
            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            # Update log
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
            email_log.save()
            
            logger.info(f"Email sent to {user.email}: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {str(e)}")
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.save()
    
    @staticmethod
    def send_sms_notification(user, sms_type, message):
        """
        Send SMS notification
        NOTE: Integrate with SMS provider (Twilio, etc.)
        """
        try:
            # Create SMS log
            sms_log = SMSLog.objects.create(
                recipient=user,
                phone_number=getattr(user, 'phone_number', ''),
                message=message,
                sms_type=sms_type,
            )
            # Try to send via Twilio if configured
            twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
            twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            twilio_from = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

            if twilio_sid and twilio_token and twilio_from:
                try:
                    from twilio.rest import Client

                    client = Client(twilio_sid, twilio_token)
                    resp = client.messages.create(
                        body=message,
                        from_=twilio_from,
                        to=sms_log.phone_number
                    )

                    sms_log.status = 'sent'
                    sms_log.sent_at = timezone.now()
                    sms_log.external_id = getattr(resp, 'sid', '') if hasattr(sms_log, 'external_id') else ''
                    sms_log.save()
                    logger.info(f"SMS sent to {sms_log.phone_number}")
                except Exception as e:
                    logger.error(f"Twilio SMS failed for {sms_log.phone_number}: {e}")
                    sms_log.status = 'failed'
                    sms_log.error_message = str(e)
                    sms_log.save()
            else:
                # Twilio not configured; leave as pending and log
                sms_log.status = 'pending'
                sms_log.save()
                logger.info(f"SMS provider not configured; saved SMS as pending for {sms_log.phone_number}")
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {getattr(user, 'phone_number', '')}: {str(e)}")
            try:
                sms_log.status = 'failed'
                sms_log.error_message = str(e)
                sms_log.save()
            except Exception:
                # If sms_log creation failed, nothing more we can do here
                pass

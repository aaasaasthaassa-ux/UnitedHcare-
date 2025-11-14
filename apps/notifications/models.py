from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    """
    In-app notifications for users
    """
    NOTIFICATION_TYPES = (
        ('appointment_booked', 'Appointment Booked'),
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_completed', 'Appointment Completed'),
        ('payment_received', 'Payment Received'),
        ('payment_pending', 'Payment Pending'),
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('rental_started', 'Rental Started'),
        ('rental_due', 'Rental Due Soon'),
        ('rental_overdue', 'Rental Overdue'),
        ('system_alert', 'System Alert'),
        ('welcome', 'Welcome Message'),
    )
    
    # Recipient
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    
    # Notification details
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related object (generic foreign key)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Action URL
    action_url = models.CharField(max_length=500, blank=True)
    action_text = models.CharField(max_length=100, default='View Details')
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, 
                          related_object=None, action_url='', action_text='View Details'):
        """Helper method to create notifications"""
        notification = cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            content_object=related_object,
            action_url=action_url,
            action_text=action_text,
        )
        return notification


class EmailLog(models.Model):
    """
    Log of sent emails
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    
    recipient = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='emails'
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    email_type = models.CharField(max_length=50)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} to {self.recipient.email}"


class SMSLog(models.Model):
    """
    Log of sent SMS messages
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    
    recipient = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='sms_messages'
    )
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    sms_type = models.CharField(max_length=50)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS to {self.phone_number}"


class NotificationPreference(models.Model):
    """
    User notification preferences
    """
    user = models.OneToOneField(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    
    # In-app notifications
    enable_in_app = models.BooleanField(default=True)
    
    # Email notifications
    enable_email = models.BooleanField(default=True)
    appointment_emails = models.BooleanField(default=True)
    order_emails = models.BooleanField(default=True)
    payment_emails = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # SMS notifications
    enable_sms = models.BooleanField(default=True)
    appointment_sms = models.BooleanField(default=True)
    order_sms = models.BooleanField(default=True)
    payment_sms = models.BooleanField(default=True)
    
    # Push notifications (for future mobile app)
    enable_push = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

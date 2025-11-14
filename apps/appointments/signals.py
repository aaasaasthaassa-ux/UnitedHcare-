from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.appointments.models import Appointment, PersonalAppointment


@receiver(post_save, sender=Appointment)
def appointment_created(sender, instance, created, **kwargs):
    """
    Send notification when appointment is created
    """
    if created:
        # TODO: Send email/SMS notification (deferred to Celery task)
        pass


@receiver(pre_save, sender=Appointment)
def appointment_status_changed(sender, instance, **kwargs):
    """
    Detect status changes and enqueue notifications
    """
    if not instance.pk:
        return
    try:
        old_instance = Appointment.objects.get(pk=instance.pk)
    except Appointment.DoesNotExist:
        return

    if old_instance.status != instance.status:
        # TODO: enqueue status change notification
        pass


@receiver(post_save, sender=PersonalAppointment)
def personal_appointment_notification(sender, instance, created, **kwargs):
    """
    Send notifications for personal appointments
    """
    try:
        from apps.notifications.services import NotificationService
    except Exception:
        NotificationService = None

    # Helper to safely call NotificationService if available
    def _notify(**kwargs):
        if NotificationService:
            try:
                NotificationService.send_notification(**kwargs)
            except Exception:
                # avoid raising during save
                pass

    if created:
        # Notify patient
        _notify(
            user=instance.patient,
            notification_type='appointment_booked',
            title='Personal Appointment Request Sent',
            message=f'Your appointment request with {instance.provider.get_full_name()} has been sent for {instance.appointment_date}.',
            related_object=instance,
            action_url=f'/appointments/personal/{instance.id}/',
            send_email=True,
            send_sms=True
        )
        
        # Notify provider
        _notify(
            user=instance.provider,
            notification_type='appointment_booked',
            title='New Appointment Request',
            message=f'New appointment request from {instance.patient.get_full_name()} for {instance.appointment_date}.',
            related_object=instance,
            action_url=f'/appointments/personal/{instance.id}/',
            send_email=True
        )
    else:
        # Check status changes
        if instance.status == 'confirmed':
            _notify(
                user=instance.patient,
                notification_type='appointment_confirmed',
                title='Appointment Confirmed',
                message=f'Your appointment with {instance.provider.get_full_name()} has been confirmed for {instance.appointment_date} at {instance.appointment_time}.',
                related_object=instance,
                action_url=f'/appointments/personal/{instance.id}/',
                send_email=True,
                send_sms=True
            )
        
        elif instance.status == 'completed':
            _notify(
                user=instance.patient,
                notification_type='appointment_completed',
                title='Appointment Completed',
                message=f'Your appointment with {instance.provider.get_full_name()} has been completed. Please leave a review!',
                related_object=instance,
                action_url=f'/appointments/personal/{instance.id}/review/',
                send_email=True
            )
        
        elif 'cancelled' in instance.status:
            # notify the other party
            other_user = instance.provider if instance.status == 'cancelled_by_patient' else instance.patient
            _notify(
                user=other_user,
                notification_type='appointment_cancelled',
                title='Appointment Cancelled',
                message=f'The appointment for {instance.appointment_date} has been cancelled.',
                related_object=instance,
                action_url=f'/appointments/personal/{instance.id}/',
                send_email=True,
                send_sms=True
            )

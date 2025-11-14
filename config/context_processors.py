def site_settings(request):
    """
    Add global site settings to template context
    """
    from django.conf import settings
    
    return {
        'SITE_NAME': 'UH Care',
        'SITE_TAGLINE': 'United Home Care',
        'CURRENCY': 'NPR',
        'CURRENCY_SYMBOL': 'रू',
        'SUPPORT_EMAIL': 'support@uhcare.com.np',
        'SUPPORT_PHONE': '+977-9800000000',
    }


def user_context(request):
    """
    Add user-specific context
    """
    context = {}
    
    if request.user.is_authenticated:
        # Get unread notifications count (placeholder)
        context['unread_notifications'] = 0
        
        # Get pending appointments count
        if getattr(request.user, 'role', None) == 'patient':
            from apps.appointments.models import Appointment
            context['pending_appointments_count'] = Appointment.objects.filter(
                patient=request.user,
                status='pending'
            ).count()
        elif getattr(request.user, 'role', None) == 'provider':
            from apps.appointments.models import Appointment
            context['pending_requests_count'] = Appointment.objects.filter(
                status='pending',
                provider__isnull=True
            ).count()
    
    return context


def appointment_types(request):
    """
    Make appointment types distinction clear in templates
    """
    return {
        'has_service_bookings': True,  # Services can be booked
        'has_personal_appointments': True,  # Direct appointments with providers
    }

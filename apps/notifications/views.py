from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification, NotificationPreference
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string


@login_required
def notification_list(request):
    """
    Display all notifications for user
    """
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by read status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    context = {
        'notifications': notifications,
        'filter_type': filter_type,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    
    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """
    Mark notification as read (AJAX)
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    })


@login_required
@require_POST
def mark_all_as_read(request):
    """
    Mark all notifications as read
    """
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'message': 'All notifications marked as read'
    })


@login_required
@require_POST
def delete_notification(request, notification_id):
    """
    Delete a notification
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Notification deleted'
    })


@login_required
def notification_preferences(request):
    """
    Manage notification preferences
    """
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        prefs.enable_in_app = request.POST.get('enable_in_app') == 'on'
        prefs.enable_email = request.POST.get('enable_email') == 'on'
        prefs.appointment_emails = request.POST.get('appointment_emails') == 'on'
        prefs.order_emails = request.POST.get('order_emails') == 'on'
        prefs.payment_emails = request.POST.get('payment_emails') == 'on'
        prefs.marketing_emails = request.POST.get('marketing_emails') == 'on'
        prefs.enable_sms = request.POST.get('enable_sms') == 'on'
        prefs.appointment_sms = request.POST.get('appointment_sms') == 'on'
        prefs.order_sms = request.POST.get('order_sms') == 'on'
        prefs.payment_sms = request.POST.get('payment_sms') == 'on'
        prefs.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Preferences saved successfully'
        })
    
    context = {
        'preferences': prefs,
    }
    
    return render(request, 'notifications/preferences.html', context)


@login_required
def get_unread_count(request):
    """
    Get unread notification count (AJAX)
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return JsonResponse({
        'unread_count': count
    })


@login_required
def recent_notifications(request):
    """
    Return a small HTML snippet with recent notifications for the navbar dropdown
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:6]
    context = {'notifications': notifications}
    html = render_to_string('notifications/recent.html', context, request=request)
    return HttpResponse(html)

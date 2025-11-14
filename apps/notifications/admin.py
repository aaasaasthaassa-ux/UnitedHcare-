from django.contrib import admin
from .models import Notification, EmailLog, SMSLog, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recipient', 'email_type', 'status', 'sent_at']
    list_filter = ['status', 'email_type', 'created_at']
    search_fields = ['subject', 'recipient__email', 'message']
    readonly_fields = ['created_at', 'sent_at']
    date_hierarchy = 'created_at'


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'recipient', 'sms_type', 'status', 'sent_at']
    list_filter = ['status', 'sms_type', 'created_at']
    search_fields = ['phone_number', 'message', 'recipient__email']
    readonly_fields = ['created_at', 'sent_at']
    date_hierarchy = 'created_at'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'enable_in_app', 'enable_email', 'enable_sms']
    list_filter = ['enable_in_app', 'enable_email', 'enable_sms']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

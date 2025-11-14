from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EquipmentCategory, Equipment, EquipmentRental, 
    EquipmentPurchase, EquipmentWishlist
)


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'equipment_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def equipment_count(self, obj):
        return obj.equipments.count()
    equipment_count.short_description = 'Equipment'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'available_units', 'price_per_day', 'purchase_price', 'is_active'
    ]
    list_filter = ['category', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['total_rentals', 'total_purchases', 'created_at', 'updated_at', 'image_preview', 'image_link']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category')
        }),
        ('Product Details', {
            'fields': ('description', 'image', 'image_url', 'image_preview', 'image_link')
        }),
        ('Pricing & Stock', {
            'fields': ('price_per_day', 'rent_price_weekly', 'rent_price_monthly', 'security_deposit', 'purchase_price')
        }),
        ('Stock', {
            'fields': ('total_units', 'available_units')
        }),
    )

    def image_preview(self, obj):
        """Show a small preview of the equipment image in the admin change view."""
        if obj and getattr(obj, 'image', None):
            try:
                return format_html(
                    '<img src="{}" style="max-height:200px; max-width:300px; object-fit:contain;" />',
                    obj.image.url
                )
            except Exception:
                return '(Image not available)'
        return '(No image)'
    image_preview.short_description = 'Image'

    def image_link(self, obj):
        """Show the direct URL for the image as a clickable link (readonly helper)."""
        # Prefer a configured `image_url` field on the model if present, otherwise fall back to uploaded image URL
        if obj:
            # if model has image_url (external link), show that
            if getattr(obj, 'image_url', None):
                return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', obj.image_url, obj.image_url)

            if getattr(obj, 'image', None):
                try:
                    url = obj.image.url
                    return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, url)
                except Exception:
                    return '(Image URL not available)'

        return '(No image)'
    image_link.short_description = 'Image URL'


@admin.register(EquipmentRental)
class EquipmentRentalAdmin(admin.ModelAdmin):
    list_display = [
        'rental_number', 'customer', 'equipment', 'rental_period', 'start_date', 'end_date', 'total_amount', 'status'
    ]
    list_filter = ['status', 'rental_period', 'start_date']
    search_fields = ['rental_number', 'customer__email', 'equipment__name']
    readonly_fields = ['rental_number', 'rental_days', 'created_at', 'updated_at']

    fieldsets = (
        ('Rental Information', {
            'fields': ('rental_number', 'customer', 'equipment', 'status')
        }),
        ('Rental Details', {
            'fields': ('rental_period', 'quantity', 'start_date', 'end_date')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'delivery_phone', 'delivery_instructions')
        }),
        ('Pricing', {
            'fields': ('rental_price', 'security_deposit', 'delivery_charge', 'late_fee', 'damage_charge', 'total_amount')
        }),
        ('Condition Notes', {
            'fields': ('condition_at_delivery', 'condition_at_return', 'damage_notes')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Allow staff/admin to override immutability when editing in admin
        if change:
            setattr(obj, '_allow_modification', True)
        super().save_model(request, obj, form, change)


@admin.register(EquipmentPurchase)
class EquipmentPurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'equipment', 'quantity', 'total_amount', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer__email', 'equipment__name']
    readonly_fields = ['order_number', 'subtotal', 'created_at', 'updated_at']

    fieldsets = (
        ('Purchase Information', {
            'fields': ('order_number', 'customer', 'equipment', 'quantity', 'status')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'delivery_phone', 'delivery_instructions')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'subtotal', 'delivery_charge', 'discount', 'total_amount')
        }),
        ('Warranty', {
            'fields': ('warranty_months', 'warranty_expires_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Allow staff/admin to override immutability when editing in admin
        if change:
            setattr(obj, '_allow_modification', True)
        super().save_model(request, obj, form, change)


@admin.register(EquipmentWishlist)
class EquipmentWishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'equipment', 'added_at']
    search_fields = ['user__email', 'equipment__name']

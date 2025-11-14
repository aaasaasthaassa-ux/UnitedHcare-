from django.contrib import admin
from django.utils.html import format_html
from .models import (
    MedicineCategory, Medicine, PharmacyOrder, PharmacyOrderItem,
    Cart, CartItem, PharmacyWishlist
)
from .models import PharmacyOrderActivity


@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'display_order', 'medicine_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    
    def medicine_count(self, obj):
        return obj.medicines.count()
    medicine_count.short_description = 'Medicines'


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'stock_quantity', 
        'prescription_required', 'is_active', 'stock_status'
    ]
    list_filter = ['category', 'prescription_required', 'is_active', 'unit_type']
    search_fields = ['name', 'generic_name', 'manufacturer']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['total_sales', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'generic_name', 'manufacturer', 'category')
        }),
        ('Product Details', {
            'fields': ('description', 'uses', 'side_effects', 'dosage_instructions', 'warnings')
        }),
        ('Unit & Packaging', {
            'fields': ('unit_type', 'strength', 'package_size')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Prescription', {
            'fields': ('prescription_required',)
        }),
        ('Media', {
            'fields': ('image', 'image_url',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('total_sales', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            color = '#FF3B30'
            status = 'Out of Stock'
        elif obj.is_low_stock:
            color = '#FF9500'
            status = 'Low Stock'
        else:
            color = '#34C759'
            status = 'In Stock'
        
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, status
        )
    stock_status.short_description = 'Stock Status'


class PharmacyOrderItemInline(admin.TabularInline):
    model = PharmacyOrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(PharmacyOrder)
class PharmacyOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'total_amount', 
        'status', 'prescription_verified', 'created_at'
    ]
    list_filter = ['status', 'prescription_verified', 'created_at']
    search_fields = ['order_number', 'customer__email', 'customer__first_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'total_amount']
    inlines = [PharmacyOrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'delivery_phone', 'delivery_instructions')
        }),
        ('Prescription', {
            'fields': ('prescription_image', 'prescription_verified')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_charge', 'discount', 'total_amount')
        }),
        ('Tracking', {
            'fields': ('delivered_at', 'delivery_person')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'internal_notes', 'cancellation_reason')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Allow staff/admin to override immutability when editing in admin
        if change:
            setattr(obj, '_allow_modification', True)
        super().save_model(request, obj, form, change)


@admin.register(PharmacyOrderActivity)
class PharmacyOrderActivityAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['order__order_number', 'title', 'message']
    readonly_fields = ['created_at']

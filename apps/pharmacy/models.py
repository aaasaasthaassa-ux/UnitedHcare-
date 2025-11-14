from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class MedicineCategory(models.Model):
    """
    Categories for medicines
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'medicine_categories'
        verbose_name_plural = 'Medicine Categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class Medicine(models.Model):
    """
    Medicine/Pharmacy products
    """
    UNIT_CHOICES = (
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream/Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('powder', 'Powder'),
        ('other', 'Other'),
    )
    
    PRESCRIPTION_CHOICES = (
        ('required', 'Prescription Required'),
        ('not_required', 'Over the Counter'),
    )
    
    category = models.ForeignKey(MedicineCategory, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    generic_name = models.CharField(max_length=200, blank=True, help_text="Scientific/generic name")
    manufacturer = models.CharField(max_length=200, blank=True)
    
    # Product details
    description = models.TextField()
    uses = models.TextField(help_text="What is this medicine used for?")
    side_effects = models.TextField(blank=True, help_text="Possible side effects")
    dosage_instructions = models.TextField(help_text="How to use this medicine")
    warnings = models.TextField(blank=True, help_text="Warnings and precautions")
    
    # Unit & Packaging
    unit_type = models.CharField(max_length=20, choices=UNIT_CHOICES, default='tablet')
    strength = models.CharField(max_length=50, help_text="e.g., 500mg, 10ml")
    package_size = models.PositiveIntegerField(help_text="Number of units per package")
    
    # Pricing & Stock
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    
    # Prescription
    prescription_required = models.CharField(
        max_length=20,
        choices=PRESCRIPTION_CHOICES,
        default='not_required'
    )
    
    # Media
    image_url = models.URLField(blank=True, null=True)
    # Local image upload for product images
    image = models.ImageField(upload_to='pharmacy/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_sales = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'medicines'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['generic_name']),
        ]
        ordering = ['-is_featured', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.strength}"
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold


class PharmacyOrder(models.Model):
    """
    Pharmacy delivery orders
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    # Customer
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='pharmacy_orders')
    
    # Order details
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Delivery address
    delivery_address = models.TextField()
    delivery_phone = models.CharField(max_length=15)
    delivery_instructions = models.TextField(blank=True)
    
    # Prescription
    prescription_image = models.URLField(blank=True, null=True, help_text="Upload prescription if required")
    prescription_verified = models.BooleanField(default=False)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Tracking
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_person = models.CharField(max_length=100, blank=True)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pharmacy_orders'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        # Prevent modifying critical order fields once order is no longer pending
        if self.pk:
            try:
                old = PharmacyOrder.objects.get(pk=self.pk)
            except PharmacyOrder.DoesNotExist:
                old = None

            if old and old.status != 'pending' and not getattr(self, '_allow_modification', False):
                locked_fields = [
                    'delivery_address', 'delivery_phone', 'delivery_instructions', 'prescription_image', 'customer_notes'
                ]
                for f in locked_fields:
                    if getattr(old, f) != getattr(self, f):
                        raise ValidationError('This order cannot be modified after it has been confirmed/processed. To change your order, please place a new one.')

        if not self.order_number:
            import uuid
            self.order_number = f"PH{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total
        self.total_amount = self.subtotal + self.delivery_charge - self.discount
        # Detect changes for activity logging
        is_new = self.pk is None
        old_status = None
        old_prescription_verified = None
        if not is_new:
            try:
                old = PharmacyOrder.objects.get(pk=self.pk)
                old_status = old.status
                old_prescription_verified = old.prescription_verified
            except PharmacyOrder.DoesNotExist:
                old = None

        super().save(*args, **kwargs)

        # Create activities
        try:
            from .models import PharmacyOrderActivity
        except Exception:
            PharmacyOrderActivity = None

        if PharmacyOrderActivity:
            if is_new:
                PharmacyOrderActivity.objects.create(
                    order=self,
                    title='Order placed',
                    message='Your order has been placed successfully.'
                )

            # Prescription uploaded on create
            if is_new and self.prescription_image:
                PharmacyOrderActivity.objects.create(
                    order=self,
                    title='Prescription uploaded',
                    message='Prescription uploaded for verification.'
                )

            # Prescription verified
            if old_prescription_verified is not None and not old_prescription_verified and self.prescription_verified:
                PharmacyOrderActivity.objects.create(
                    order=self,
                    title='Prescription verified',
                    message='Prescription has been verified by our team.'
                )

            # Status change
            if old_status is not None and old_status != self.status:
                PharmacyOrderActivity.objects.create(
                    order=self,
                    title=f'Order {self.get_status_display()}',
                    message=f'Order status updated to {self.get_status_display()}.'
                )


class PharmacyOrderItem(models.Model):
    """
    Items in a pharmacy order
    """
    order = models.ForeignKey(PharmacyOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='order_items')
    
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'pharmacy_order_items'
        unique_together = ('order', 'medicine')
    
    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class PharmacyOrderActivity(models.Model):
    """Activity / timeline entries for a PharmacyOrder."""
    ACTIVITY_CHOICES = (
        ('placed', 'Order Placed'),
        ('payment', 'Payment'),
        ('prescription_uploaded', 'Prescription Uploaded'),
        ('prescription_verified', 'Prescription Verified'),
        ('status', 'Status Update'),
        ('delivered', 'Delivered'),
        ('other', 'Other'),
    )

    order = models.ForeignKey(PharmacyOrder, on_delete=models.CASCADE, related_name='activities')
    actor = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL)
    activity_type = models.CharField(max_length=40, choices=ACTIVITY_CHOICES, default='other')
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pharmacy_order_activities'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.title}"


# CART, WISHLIST and other shared models (pharmacy side)
class Cart(models.Model):
    """
    Shopping cart for users
    """
    CART_TYPE_CHOICES = (
        ('pharmacy', 'Pharmacy'),
        ('equipment', 'Equipment'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='carts')
    cart_type = models.CharField(max_length=20, choices=CART_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        unique_together = ('user', 'cart_type')
    
    def __str__(self):
        return f"{self.user.username} - {self.cart_type} cart"
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def subtotal(self):
        # Ensure subtotal is a Decimal even when there are no items (sum would
        # otherwise return an int 0). Use Decimal start to avoid mixing types
        # which can raise TypeError when adding Decimal and float.
        return sum((item.total_price for item in self.items.all()), Decimal('0.00'))


class CartItem(models.Model):
    """
    Items in shopping cart
    """
    ITEM_TYPE_CHOICES = (
        ('medicine', 'Medicine'),
        ('equipment_rent', 'Equipment Rental'),
        ('equipment_buy', 'Equipment Purchase'),
    )
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    
    # References (one will be populated based on item_type)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True, blank=True)
    equipment = models.ForeignKey('equipment.Equipment', on_delete=models.CASCADE, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # For equipment rentals
    rental_period = models.CharField(max_length=20, blank=True)
    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
    
    def __str__(self):
        if self.medicine:
            return f"{self.medicine.name} x {self.quantity}"
        elif self.equipment:
            return f"{self.equipment.name} x {self.quantity}"
        return f"Cart item #{self.id}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class PharmacyWishlist(models.Model):
    """
    Wishlist for pharmacy products
    """
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='pharmacy_wishlist')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pharmacy_wishlists'
        unique_together = ('user', 'medicine')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.medicine.name}"


# Note: Equipment wishlist lives in apps.equipment.models to avoid cross-app db_table/name clashes.

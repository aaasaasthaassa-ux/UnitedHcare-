from django import forms
from .models import EquipmentRental, EquipmentPurchase
from datetime import date, timedelta


class EquipmentRentalForm(forms.ModelForm):
    """
    Form for renting equipment
    """
    class Meta:
        model = EquipmentRental
        fields = [
            'rental_period',
            'quantity',
            'start_date',
            'end_date',
            'delivery_address',
            'delivery_phone',
            'delivery_instructions',
            'customer_notes',
        ]
        widgets = {
            'rental_period': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Delivery address'
            }),
            'delivery_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '98XXXXXXXX'
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special instructions (optional)'
            }),
            'customer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.equipment = kwargs.pop('equipment', None)
        super().__init__(*args, **kwargs)
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        # equipment model uses `available_units` (not stock_quantity). Use
        # available_units to validate requested quantity.
        if self.equipment and quantity > getattr(self.equipment, 'available_units', 0):
            raise forms.ValidationError(
                f'Only {getattr(self.equipment, "available_units", 0)} units available.'
            )
        return quantity
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError('End date must be after start date.')
            
            if start_date < date.today():
                raise forms.ValidationError('Start date cannot be in the past.')
        
        return cleaned_data
    
    def save(self, commit=True):
        rental = super().save(commit=False)
        
        # Calculate rental price based on period
        if self.equipment:
            rental_days = (rental.end_date - rental.start_date).days + 1
            
            if rental.rental_period == 'daily':
                rental.rental_price = self.equipment.price_per_day * rental_days * rental.quantity
            elif rental.rental_period == 'weekly':
                weeks = (rental_days + 6) // 7
                rental.rental_price = getattr(self.equipment, 'rent_price_weekly', 0) * weeks * rental.quantity
            elif rental.rental_period == 'monthly':
                months = (rental_days + 29) // 30
                rental.rental_price = getattr(self.equipment, 'rent_price_monthly', 0) * months * rental.quantity
            
            rental.security_deposit = getattr(self.equipment, 'security_deposit', 0) * rental.quantity
        
        if commit:
            rental.save()
        return rental


class EquipmentPurchaseForm(forms.ModelForm):
    """
    Form for purchasing equipment
    """
    class Meta:
        model = EquipmentPurchase
        fields = [
            'quantity',
            'delivery_address',
            'delivery_phone',
            'delivery_instructions',
            'customer_notes',
        ]
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Delivery address'
            }),
            'delivery_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '98XXXXXXXX'
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special instructions (optional)'
            }),
            'customer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.equipment = kwargs.pop('equipment', None)
        super().__init__(*args, **kwargs)
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        # equipment model uses `available_units` (not stock_quantity). Use
        # available_units to validate requested quantity.
        if self.equipment and quantity > getattr(self.equipment, 'available_units', 0):
            raise forms.ValidationError(
                f'Only {getattr(self.equipment, "available_units", 0)} units available.'
            )
        return quantity

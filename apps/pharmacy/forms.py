from django import forms
from .models import PharmacyOrder, Medicine
from datetime import date


class PharmacyOrderForm(forms.ModelForm):
    """
    Form for placing pharmacy orders
    """
    class Meta:
        model = PharmacyOrder
        fields = [
            'delivery_address',
            'delivery_phone',
            'delivery_instructions',
            'prescription_image',
            'customer_notes',
        ]
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your complete delivery address'
            }),
            'delivery_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '98XXXXXXXX'
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special delivery instructions (optional)'
            }),
            'prescription_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'customer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes (optional)'
            }),
        }

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.services.models import ServiceCategory, Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample service data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Nursing Care',
                'description': 'Professional nursing services at home',
            },
            {
                'name': 'Physiotherapy & Rehabilitation',
                'description': 'Physical therapy and recovery services',
            },
            {
                'name': 'Elderly & Geriatric Care',
                'description': 'Specialized care for seniors',
            },
            {
                'name': 'Chronic Illness Management',
                'description': 'Long-term care for chronic conditions',
            },
        ]
        
        for idx, cat_data in enumerate(categories_data):
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'display_order': idx,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category.name}'))
        
        # Create services
        nursing = ServiceCategory.objects.get(name='Nursing Care')
        physio = ServiceCategory.objects.get(name='Physiotherapy & Rehabilitation')
        elderly = ServiceCategory.objects.get(name='Elderly & Geriatric Care')
        chronic = ServiceCategory.objects.get(name='Chronic Illness Management')
        
        services_data = [
            {
                'category': nursing,
                'name': 'Skilled Nursing Care',
                'short_description': 'Professional nursing care at home',
                'description': 'Comprehensive nursing services including medication management, vital monitoring, wound care, and health assessment.',
                'base_price': Decimal('1500.00'),
                'duration_unit': 'session',
                'what_included': '• Vital signs monitoring\n• Medication administration\n• Wound dressing\n• Health assessment\n• Care plan development',
                'is_featured': True,
            },
            {
                'category': physio,
                'name': 'Home Physiotherapy',
                'short_description': 'Physical therapy at home',
                'description': 'Professional physiotherapy sessions for rehabilitation, recovery, and mobility improvement.',
                'base_price': Decimal('2000.00'),
                'duration_unit': 'session',
                'what_included': '• Exercise therapy\n• Pain management\n• Mobility training\n• Recovery assessment\n• Home exercise program',
                'is_featured': True,
            },
            {
                'category': elderly,
                'name': 'Elderly Care Services',
                'short_description': 'Compassionate care for seniors',
                'description': 'Comprehensive care for elderly patients including daily assistance, companionship, and health monitoring.',
                'base_price': Decimal('1800.00'),
                'duration_unit': 'day',
                'what_included': '• Daily living assistance\n• Companionship\n• Medication reminders\n• Meal assistance\n• Safety monitoring',
                'is_featured': True,
            },
            {
                'category': nursing,
                'name': 'Post-Surgery Home Care',
                'short_description': 'Recovery care after surgery',
                'description': 'Specialized post-operative care at home to ensure safe and comfortable recovery.',
                'base_price': Decimal('2500.00'),
                'duration_unit': 'session',
                'what_included': '• Wound care\n• Pain management\n• Medication administration\n• Mobility assistance\n• Recovery monitoring',
                'is_featured': False,
            },
            {
                'category': chronic,
                'name': 'Diabetes Management',
                'short_description': 'Diabetes care at home',
                'description': 'Professional diabetes management including monitoring, education, and support.',
                'base_price': Decimal('1200.00'),
                'duration_unit': 'session',
                'what_included': '• Blood sugar monitoring\n• Insulin administration\n• Diet counseling\n• Lifestyle guidance\n• Complication screening',
                'is_featured': False,
            },
        ]
        
        for service_data in services_data:
            defaults = service_data.copy()
            defaults.pop('category')
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    **defaults,
                    'slug': slugify(service_data['name']),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created service: {service.name}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))

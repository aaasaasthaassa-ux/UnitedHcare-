from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.appointments.models import ProviderSchedule
from datetime import time


class Command(BaseCommand):
    help = 'Create sample schedules for providers'

    def handle(self, *args, **kwargs):
        providers = User.objects.filter(role='provider', is_active=True)
        
        for provider in providers:
            # Create Monday to Friday, 9 AM to 5 PM schedule
            for day in range(5):  # Monday to Friday
                ProviderSchedule.objects.get_or_create(
                    provider=provider,
                    day_of_week=day,
                    start_time=time(9, 0),
                    defaults={
                        'end_time': time(17, 0),
                        'slot_duration': 30,
                        'is_available': True,
                    }
                )
            
            # Saturday morning only
            ProviderSchedule.objects.get_or_create(
                provider=provider,
                day_of_week=5,
                start_time=time(9, 0),
                defaults={
                    'end_time': time(13, 0),
                    'slot_duration': 30,
                    'is_available': True,
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✅ Provider schedules created!'))

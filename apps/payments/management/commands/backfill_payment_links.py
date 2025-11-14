from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.payments.models import Payment


class Command(BaseCommand):
    help = 'Backfill Payment foreign keys to pharmacy orders and equipment purchases/rentals when possible'

    def handle(self, *args, **options):
        self.stdout.write('Starting backfill of payment links...')
        unmatched = 0
        linked = 0

        # Define time window to search orders around payment creation
        window = timedelta(days=3)

        # Backfill pharmacy orders
        from apps.pharmacy.models import PharmacyOrder
        payments = Payment.objects.filter(pharmacy_order__isnull=True, appointment__isnull=True)
        for p in payments:
            # try to match pharmacy order by customer and amount in time window
            candidates = PharmacyOrder.objects.filter(
                customer=p.patient,
                total_amount=p.amount
            )
            if p.created_at:
                candidates = candidates.filter(created_at__range=(p.created_at - window, p.created_at + window))

            if candidates.count() == 1:
                order = candidates.first()
                p.pharmacy_order = order
                p.save()
                linked += 1
                self.stdout.write(f'Linked Payment {p.id} -> PharmacyOrder {order.id}')

        # Backfill equipment purchases
        from apps.equipment.models import EquipmentPurchase, EquipmentRental
        payments = Payment.objects.filter(equipment_purchase__isnull=True, equipment_rental__isnull=True, appointment__isnull=True, pharmacy_order__isnull=True)
        for p in payments:
            # try purchase
            candidates = EquipmentPurchase.objects.filter(
                customer=p.patient,
                total_amount=p.amount
            )
            if p.created_at:
                candidates = candidates.filter(created_at__range=(p.created_at - window, p.created_at + window))
            if candidates.count() == 1:
                purchase = candidates.first()
                p.equipment_purchase = purchase
                p.save()
                linked += 1
                self.stdout.write(f'Linked Payment {p.id} -> EquipmentPurchase {purchase.id}')
                continue

            # try rental
            candidates = EquipmentRental.objects.filter(
                customer=p.patient,
                total_amount=p.amount
            )
            if p.created_at:
                candidates = candidates.filter(created_at__range=(p.created_at - window, p.created_at + window))
            if candidates.count() == 1:
                rental = candidates.first()
                p.equipment_rental = rental
                p.save()
                linked += 1
                self.stdout.write(f'Linked Payment {p.id} -> EquipmentRental {rental.id}')
                continue

            unmatched += 1

        self.stdout.write(self.style.SUCCESS(f'Backfill complete: linked={linked}, unmatched={unmatched}'))

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.payments.models import Payment


class Command(BaseCommand):
    help = (
        "Report payments with payment_method='cash' and optionally set them to NULL. "
        "Run with --apply to perform changes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually set payment_method to NULL for matching payments.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit how many payments to modify when --apply is used (0 = no limit).",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        limit = options["limit"]

        qs = Payment.objects.filter(payment_method="cash")
        total = qs.count()

        self.stdout.write(self.style.NOTICE(f"Found {total} payments with payment_method='cash'."))

        if total == 0:
            return

        # Show a brief sample
        sample = qs.order_by("-created_at")[:10]
        self.stdout.write("Latest 10 matching payments:")
        for p in sample:
            ref = None
            if p.appointment_id:
                ref = f"appointment:{p.appointment_id}"
            elif p.pharmacy_order_id:
                ref = f"pharmacy:{p.pharmacy_order.order_number if p.pharmacy_order else p.pharmacy_order_id}"
            elif p.equipment_purchase_id:
                ref = f"equipment_purchase:{p.equipment_purchase_id}"
            elif p.equipment_rental_id:
                ref = f"equipment_rental:{p.equipment_rental_id}"
            else:
                ref = f"payment:{p.id}"

            self.stdout.write(f" - id={p.id} user={p.patient_id} amount={p.amount} created_at={p.created_at} ref={ref}")

        if not apply_changes:
            self.stdout.write(self.style.WARNING("Dry-run complete. No changes made. Rerun with --apply to clear these fields."))
            return

        # Confirm and apply
        to_change = qs.order_by("-created_at")
        if limit and limit > 0:
            to_change = to_change[:limit]

        changed = 0
        with transaction.atomic():
            for p in to_change:
                p.payment_method = None
                p.save(update_fields=["payment_method", "updated_at"])  # update timestamp as well
                changed += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {changed} payments (payment_method set to NULL)."))

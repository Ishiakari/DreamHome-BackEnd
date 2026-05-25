from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.leases.models import LeaseAgreement
from apps.payments.models import Payment
from django.db.models import Sum

class Command(BaseCommand):
    help = "Applies a monthly late fee to active leases with outstanding balances"

    def add_arguments(self, parser):
        parser.add_argument(
            '--fee',
            type=float,
            default=50.00,
            help='The late fee amount to apply (default: 50.00)'
        )

    def handle(self, *args, **options):
        fee = options['fee']
        today = timezone.localdate()
        
        self.stdout.write(f"Running late fee application for date: {today} with fee: {fee}")
        
        # 1. Get all active leases (rent_finish >= today)
        active_leases = LeaseAgreement.objects.filter(rent_finish__gte=today)
        
        applied_count = 0
        
        for lease in active_leases:
            # 2. Calculate outstanding balance
            total_due = lease.monthly_rent * lease.duration
            total_paid = lease.payments.aggregate(total=Sum('amount_paid'))['total'] or 0
            outstanding_balance = total_due - total_paid
            
            if outstanding_balance > 0:
                # 3. Apply penalty
                penalty = Payment.objects.create(
                    lease=lease,
                    amount_paid=-fee,  # Negative payment increases outstanding balance
                    payment_method=Payment.PaymentMethod.PENALTY,
                    payment_date=timezone.now(),
                    status=Payment.PaymentStatus.PENALTY,
                    processed_by_staff=lease.staff_no
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f"Applied {fee} penalty ({penalty.payment_no}) to Lease {lease.lease_no} "
                    f"(Renter: {lease.renter_no.first_name} {lease.renter_no.last_name}, Outstanding: {outstanding_balance})"
                ))
                applied_count += 1
                
        self.stdout.write(self.style.SUCCESS(f"Successfully applied late fees to {applied_count} leases."))

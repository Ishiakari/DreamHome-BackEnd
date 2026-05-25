from django.db import models
from django.utils import timezone

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'Cash', 'Cash'
        CARD = 'Card', 'Credit/Debit Card'
        TRANSFER = 'Transfer', 'Bank Transfer'
        CHECK = 'Check', 'Check'
        PENALTY = 'Late Fee Penalty', 'Late Fee Penalty'

    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'
        REFUNDED = 'Refunded', 'Refunded'
        PENALTY = 'Penalty', 'Late Fee Penalty'

    payment_no = models.CharField(
        max_length=20, 
        primary_key=True, 
        editable=False,
        blank=True,
        help_text="Unique payment identifier."
    )
    
    # 🌟 FIX: Updated reference to exactly match your LeaseAgreement class
    lease = models.ForeignKey(
        'leases.LeaseAgreement', 
        on_delete=models.PROTECT, 
        related_name='payments',
        db_column='lease_no' # Keeps the database column named 'lease_no' to match your diagram
    )
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_date = models.DateTimeField(default=timezone.now)
    
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    
    status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    
    processed_by_staff = models.ForeignKey(
        'users.Staff', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='processed_payments',
        db_column='processed_by_staff_no'
    )
 
    class Meta:
        db_table = 'payment' 
        ordering = ['-payment_date'] 
 
    def save(self, *args, **kwargs):
        if not self.payment_no:
            import re
            existing_ids = Payment.objects.filter(payment_no__startswith="PAY").values_list("payment_no", flat=True)
            max_seq = 0
            for pid in existing_ids:
                try:
                    num_str = re.sub(r'\D', '', pid)
                    if num_str:
                        num = int(num_str)
                        if num > max_seq:
                            max_seq = num
                except ValueError:
                    pass
            self.payment_no = f"PAY{max_seq + 1:03d}"

        super().save(*args, **kwargs)
        if self.lease:
            self.lease.update_deposit_status()

    def delete(self, *args, **kwargs):
        lease = self.lease
        super().delete(*args, **kwargs)
        if lease:
            lease.update_deposit_status()

    def __str__(self):
        # self.lease_id fetches the 'lease_no' string without making an extra database query
        return f"Payment {self.payment_no} for Lease {self.lease_id} - {self.get_status_display()}"
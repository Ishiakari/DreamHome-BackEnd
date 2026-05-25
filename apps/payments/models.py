from django.db import models
from django.utils import timezone

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'Cash', 'Cash'
        CARD = 'Card', 'Credit/Debit Card'
        TRANSFER = 'Transfer', 'Bank Transfer'
        CHECK = 'Check', 'Check'

    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'
        REFUNDED = 'Refunded', 'Refunded'

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
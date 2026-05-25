from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class LeaseAgreement(models.Model):
    # 'lease_no' is unique across all branch offices [cite: 79]
    lease_no = models.CharField(max_length=10, primary_key=True, editable=False, blank=True)
    
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_paid = models.BooleanField(default=False)
    
    rent_start = models.DateField()
    rent_finish = models.DateField()
    
    # 🌟 RULE: Min 3 months, Max 12 months (1 year) 
    duration = models.IntegerField(
        validators=[
            MinValueValidator(3, message="Minimum lease is 3 months."),
            MaxValueValidator(12, message="Maximum lease is 1 year.")
        ],
        help_text="Duration in months"
    )
    
    # Relationships
    # 🌟 RULE: Only 'Renters' can sign leases
    renter_no = models.ForeignKey(
        'users.Client', 
        on_delete=models.PROTECT, # Protect history [source 80]
        related_name='leases',
        limit_choices_to={'role': 'Renter'}
    )
    property_no = models.ForeignKey(
        'properties.Property', 
        on_delete=models.PROTECT, 
        related_name='leases',
        limit_choices_to={'status': 'Available'}
    )
    staff_no = models.ForeignKey(
        'users.Staff', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='arranged_leases',
        limit_choices_to={'position__in': ['Manager', 'Supervisor']} # [source 115]
    )
    
    class Meta:
        verbose_name_plural = "Lease Agreements"
        db_table = 'lease_agreement'
    
    def clean(self):
        super().clean()
        
        # 🌟 LOGIC CHECK: Ensure rent_start is before rent_finish
        if self.rent_start and self.rent_finish:
            if self.rent_start >= self.rent_finish:
                raise ValidationError("The rent finish date must be after the rent start date.")

        # 🌟 LOGIC CHECK: Ensure renter has an approved viewing for the property
        if hasattr(self, 'property_no_id') and hasattr(self, 'renter_no_id') and self.property_no_id and self.renter_no_id:
            is_new = self.pk is None
            property_changed = True
            renter_changed = True
            
            if not is_new:
                # Check if property or renter actually changed
                try:
                    original = LeaseAgreement.objects.get(pk=self.pk)
                    property_changed = original.property_no_id != self.property_no_id
                    renter_changed = original.renter_no_id != self.renter_no_id
                except LeaseAgreement.DoesNotExist:
                    pass

            if is_new or property_changed or renter_changed:
                from apps.properties.models import PropertyViewing
                has_approved = PropertyViewing.objects.filter(
                    property_no_id=self.property_no_id,
                    renter_no_id=self.renter_no_id,
                    status='Approved'
                ).exists()
                if not has_approved:
                    raise ValidationError(
                        "Cannot assign this lease: The renter must have an 'Approved' property viewing for this property."
                    )

    def save(self, *args, **kwargs):
        # 🌟 AUTOMATION: When a new lease is created, update the property status
        is_new = self.pk is None
        
        # Calculate deposit status based on existing payments (only if not a new lease)
        if not is_new and (not kwargs.get('update_fields') or 'deposit_paid' not in kwargs.get('update_fields')):
            total_completed = self.payments.filter(status='Completed').aggregate(
                total=models.Sum('amount_paid')
            )['total'] or 0
            self.deposit_paid = total_completed >= self.deposit
            
        super().save(*args, **kwargs) # Save the lease first
        
        if is_new and self.property_no:
            # Assuming you used the PropertyStatus TextChoices we made earlier
            self.property_no.status = 'Rented' 
            self.property_no.save()

    def update_deposit_status(self):
        if not self.pk:
            return
            
        from django.db import transaction
        with transaction.atomic():
            # Lock the lease for update to ensure concurrency safety
            lease = LeaseAgreement.objects.select_for_update().get(pk=self.pk)
            total_completed = lease.payments.filter(status='Completed').aggregate(
                total=models.Sum('amount_paid')
            )['total'] or 0
            
            is_paid = total_completed >= lease.deposit
            if lease.deposit_paid != is_paid:
                lease.deposit_paid = is_paid
                lease.save(update_fields=['deposit_paid'])
                # Also update the in-memory instance to reflect the DB change
                self.deposit_paid = is_paid

    def __str__(self):
        return f"Lease {self.lease_no} for {self.property_no.property_no}"
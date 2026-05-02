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
    
    def clean(self):
        super().clean()
        
        # 🌟 LOGIC CHECK: Ensure rent_start is before rent_finish
        if self.rent_start and self.rent_finish:
            if self.rent_start >= self.rent_finish:
                raise ValidationError("The rent finish date must be after the rent start date.")

    def save(self, *args, **kwargs):
        # 🌟 AUTOMATION: When a new lease is created, update the property status
        is_new = self.pk is None
        
        super().save(*args, **kwargs) # Save the lease first
        
        if is_new and self.property_no:
            # Assuming you used the PropertyStatus TextChoices we made earlier
            self.property_no.status = 'Rented' 
            self.property_no.save()

    def __str__(self):
        return f"Lease {self.lease_no} for {self.property.property_no}"
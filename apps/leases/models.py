from django.db import models

# Create your models here.
class LeaseAgreement(models.Model):
    lease_no = models.CharField(max_length=10, primary_key=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_paid = models.BooleanField(default=False)
    rent_start = models.DateField()
    rent_finish = models.DateField()
    duration = models.IntegerField(help_text="Duration in months")
    
    # Relationships
    renter = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='leases')
    property = models.ForeignKey('properties.PropertyForRent', on_delete=models.CASCADE, related_name='leases')
    staff = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, related_name='arranged_leases')
    
    
    def __str__(self):
        return f"Lease {self.lease_no} for {self.property}"
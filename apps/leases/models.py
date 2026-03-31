from django.db import models

# Create your models here.
class LeaseAgreement(models.Model):
    lease_no = models.CharField(max_length=10, primary_key=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
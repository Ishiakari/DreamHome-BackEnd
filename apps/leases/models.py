from django.db import models

# Create your models here.
class LeaseAgreement(models.Model):
    lease_no = models.CharField(max_length=10, primary_key=True)
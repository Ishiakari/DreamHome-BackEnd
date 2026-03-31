from django.db import models

# Create your models here.

class Staff(models.Model):
    d = 50
    


class NextOfKin(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, primary_key=True, related_name='next_of_kin')
    full_name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=50)
    
    
class Renter(models.Model):
    renter_no = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    pref_property_type = models.CharField(max_length=50, blank=True, null=True)
    max_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
class PropertyOwner(models.Model):
    owner_no = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
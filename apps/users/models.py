from django.db import models

# Create your models here.

class Staff(models.Model):
    d = 50
    


class NextOfKin(models.Model):
    d = 50
    
class Renter(models.Model):
    renter_no = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    
    
class PropertyOwner(models.Model):
    owner_no = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
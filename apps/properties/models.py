from django.db import models

# Create your models here.
class PropertyForRent(models.Model):
    property_no = models.CharField(max_length=10, primary_key=True)
    street = models.CharField(max_length=255)
    
class PropertyViewing(models.Model):
    d = 50
    
    
class PropertyInspection(models.Model):
    d = 50
    
class Advertisement(models.Model):
    d = 50
from django.db import models

# Create your models here.
class PropertyForRent(models.Model):
    property_no = models.CharField(max_length=10, primary_key=True)
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    property_type = models.CharField(max_length=50) # 'type' is a reserved Python keyword, so we use 'property_type'
    
    
    
    
        
class PropertyViewing(models.Model):
    d = 50
    
    
class PropertyInspection(models.Model):
    d = 50
    
class Advertisement(models.Model):
    d = 50
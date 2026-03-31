from django.db import models

# Create your models here.
class PropertyForRent(models.Model):
    property_no = models.CharField(max_length=10, primary_key=True)
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    property_type = models.CharField(max_length=50) # 'type' is a reserved Python keyword, so we use 'property_type'
    no_of_rooms = models.IntegerField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    
    # Relationships
    owner = models.ForeignKey('users.PropertyOwner', on_delete=models.CASCADE, related_name='properties')
    staff = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, related_name='managed_properties')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='properties')
    
    class Meta:
        verbose_name_plural = "Properties for Rent"
        
    def __str__(self):
        return f"{self.property_no} - {self.street}, {self.city}"
    
    
    
    
class PropertyViewing(models.Model):
    property = models.ForeignKey(PropertyForRent, on_delete=models.CASCADE, related_name='viewings')
    renter = models.ForeignKey('users.Renter', on_delete=models.CASCADE, related_name='viewings')
    view_date = models.DateField()
    comments = models.TextField(blank=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['property', 'renter', 'view_date'], name='unique_property_viewing')
        ]
    
    def __str__(self):
        return f"{self.renter} viewed {self.property} on {self.view_date}"
    
class PropertyInspection(models.Model):
    property = models.ForeignKey(PropertyForRent, on_delete=models.CASCADE, related_name='inspections')
    staff = models.ForeignKey('users.Staff', on_delete=models.CASCADE, related_name='inspections')
    inspection_date = models.DateField()
    comments = models.TextField(blank=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['property', 'inspection_date'], name='unique_property_inspection')
        ]
    
    def __str__(self):
        return f"Inspection for {self.property} on {self.inspection_date}"
    
class Advertisement(models.Model):
    d = 50
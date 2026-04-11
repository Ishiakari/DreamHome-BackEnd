from django.db import models
from django.core.exceptions import ValidationError

class PropertyForRent(models.Model):
    
    # 🌟 NEW: Standardized choices for data consistency
    class PropertyType(models.TextChoices):
        FLAT = 'Flat', 'Flat'
        HOUSE = 'House', 'House'
        
    class PropertyStatus(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        RENTED = 'Rented', 'Rented'
        WITHDRAWN = 'Withdrawn', 'Withdrawn'
        
    

    property_no = models.CharField(max_length=10, primary_key=True, editable=False, blank=True)
    title = models.CharField(max_length=200, help_text="e.g. Stunning 2-Bed Flat in City Centre", default="A Property for Rent")
    description = models.TextField(help_text="Full description of the property features and area.", default="A Property")
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    
    # 🌟 UPDATED: Apply choices
    property_type = models.CharField(max_length=50, choices=PropertyType.choices) 
    no_of_rooms = models.IntegerField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=PropertyStatus.choices, default=PropertyStatus.AVAILABLE)
    
    # Relationships
    # 🌟 UPDATED: Ensure only clients with the 'Owner' role can be assigned here
    owner = models.ForeignKey(
        'users.Client', 
        on_delete=models.CASCADE, 
        related_name='owned_properties',
        limit_choices_to={'role': 'Owner'}
    )
    
    staff = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, related_name='managed_properties')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='properties')
    date_withdrawn = models.DateField(blank=True, null=True, help_text="Date the property was removed from the market.")
    
    class Meta:
        verbose_name_plural = "Properties for Rent"
        
    def __str__(self):
        return f"{self.property_no} - {self.street}, {self.city}"

    def clean(self):
        super().clean()
        
        # 🌟 BUSINESS RULE: A staff member can manage a max of 20 properties
        if self.staff:
            # Count current active properties managed by this staff member
            # We exclude 'Withdrawn' properties because the staff isn't actively managing them
            current_managed_count = PropertyForRent.objects.filter(
                staff=self.staff
            ).exclude(status=self.PropertyStatus.WITHDRAWN).count()
            
            # Check if this is a new property being added, or an existing property changing staff
            if not self.pk or PropertyForRent.objects.get(pk=self.pk).staff != self.staff:
                if current_managed_count >= 20:
                    raise ValidationError({
                        "staff": f"{self.staff.first_name} {self.staff.last_name} already manages the maximum of 20 active properties."
                    })
    
class PropertyViewing(models.Model):
    property = models.ForeignKey(PropertyForRent, on_delete=models.CASCADE, related_name='viewings')
    renter = models.ForeignKey(
        'users.Client', 
        on_delete=models.CASCADE, 
        related_name='viewings',
        limit_choices_to={'role': 'Renter'}
    )
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
    property = models.ForeignKey(PropertyForRent, on_delete=models.CASCADE, related_name='advertisements')
    newspaper_name = models.CharField(max_length=150)
    advert_date = models.DateField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['property', 'newspaper_name', 'advert_date'], name='unique_property_advert')
        ]
    
    def __str__(self):
        return f"{self.property} advertised in {self.newspaper_name} on {self.advert_date}"
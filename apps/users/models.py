from django.db import models

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
    ('P', 'Prefer not to say')
]

ROLE_CHOICES = [
    ('RENTER'  , 'Renter'),
    ('PROPERTY_OWNER', 'Property Owner'),
    ('BOTH', 'Both')
]

# Create your models here.

class Staff(models.Model):
    staff_no = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    dob = models.DateField(verbose_name="Date of Birth")
    nin = models.CharField(max_length=50, verbose_name="National Insurance Number")
    position = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_joined = models.DateField()
    
    # Optional fields based on role
    typing_speed = models.IntegerField(blank=True, null=True, help_text="Secretarial staff only")
    manager_start_date = models.DateField(blank=True, null=True, help_text="Managers only")
    bonus_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    car_allowance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Relationships
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, related_name='staff')
    
    # Self-referencing Foreign Key for Supervisor
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    class Meta:
        verbose_name_plural = "Staff"
        
    def __str__(self):
        return f"{self.staff_no} - {self.first_name} {self.last_name}"

class NextOfKin(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, primary_key=True, related_name='next_of_kin')
    full_name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "Next of Kin"
        
    def __str__(self):
        return f"{self.full_name} ({self.relationship} to {self.staff.staff_no})"
    
    
class Renter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='renter_profile')
    
    renter_no = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # 🌟 NEW FIELDS
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RENTER')


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
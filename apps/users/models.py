from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import generate_client_no
from django.core.exceptions import ValidationError

# .\venv\Scripts\activate
# python manage.py makemigrations
# python manage.py migrate

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
    ('P', 'Prefer not to say')
]



CLIENT_ROLE_CHOICES = [
    ('RENTER', 'Renter'),
    ('OWNER', 'Property Owner'),
    ('BOTH', 'Both')
]

# ==========================================
# 1. STAFF MODELS
# ==========================================

class Staff(models.Model):
    # 🌟 SECURE LOGIN LINK: Handles the encrypted password and core authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    
    staff_no = models.CharField(max_length=10, primary_key=True)
    
    # 🌟 NEW FIELD: Email added for login and internal communication
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    dob = models.DateField(verbose_name="Date of Birth")
    nin = models.CharField(max_length=50, verbose_name="National Insurance Number")
    
    # Consider making this a choices field in the future for stricter consistency
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
    
    # 🌟 THE SUPERVISOR COLUMN
    supervisor = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subordinates',
        limit_choices_to={'position__icontains': 'Supervisor'}, # Ensures only supervisors can be selected
        help_text="The supervisor overseeing this staff member."
    )
    
    class Meta:
        verbose_name_plural = "Staff"
        
    def __str__(self):
        return f"{self.staff_no} - {self.first_name} {self.last_name}"

    def clean(self):
        super().clean()
        
        # 🌟 ENFORCE MAX STAFF RULE: A supervisor can manage a max of 10 staff members 
        if self.supervisor:
            current_subordinates_count = self.supervisor.subordinates.count()
            
            # Check if this is a new assignment or a change of supervisor
            if not self.pk or Staff.objects.get(pk=self.pk).supervisor != self.supervisor:
                if current_subordinates_count >= 10:
                    raise ValidationError({
                        "supervisor": f"Supervisor {self.supervisor.first_name} already manages the maximum of 10 staff members."
                    })


# ==========================================
# 2. UNIFIED CLIENT MODELS 
# ==========================================

class Client(models.Model):
    """
    A single table for anyone doing business with DreamHome.
    Eliminates duplicated columns and makes role switching easy.
    """
    # 🌟 SECURE LOGIN LINK: Handles the email and encrypted password
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='client_profile')
    
    client_no = models.CharField(
        max_length=12, 
        primary_key=True, 
    #  default=generate_client_no, 
        editable=False
    )
    # python manage.py makemigrations --empty users
    # Core Shared Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    telephone_no = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    
    # Determines what they can do on the frontend
    role = models.CharField(max_length=20, choices=CLIENT_ROLE_CHOICES, default='RENTER')

    def __str__(self):
        return f"{self.client_no} - {self.first_name} {self.last_name} ({self.role})"


class RenterRequirement(models.Model):
    """
    Holds the specific property requirements if the Client is a RENTER or BOTH.
    Matches the 'Property Requirement Details' from the case study form.
    """
    client = models.OneToOneField(Client, on_delete=models.CASCADE, primary_key=True, related_name='renter_requirements')
    
    pref_property_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Preferred Property Type") # House, Flat, ilisding nga table constrain to eith house or flat
    max_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"Requirements for {self.client.first_name} {self.client.last_name}"

class NextOfKin(models.Model):
    # A OneToOneField ensures one staff member can only have one next of kin
    staff = models.OneToOneField(
        'Staff', 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='next_of_kin'
    )
    full_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Next of Kin"

    def __str__(self):
        return f"{self.full_name} ({self.relationship} to {self.staff.staff_no})"
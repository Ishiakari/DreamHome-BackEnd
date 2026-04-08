from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import generate_client_no
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# .\venv\Scripts\activate
# python manage.py makemigrations
# python manage.py migrate

SEX_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
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

    # 🌟 strict position choices here
    class Position(models.TextChoices):
        STAFF = 'Staff', 'Standard Staff'
        MANAGER = 'Manager', 'Manager'
        SUPERVISOR = 'Supervisor', 'Supervisor'
        SECRETARY = 'Secretary', 'Secretarial Staff'

    # 🌟 SECURE LOGIN LINK: Handles the encrypted password and core authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    
    staff_no = models.CharField(max_length=10, primary_key=True, editable=False, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    dob = models.DateField(verbose_name="Date of Birth")
    nin = models.CharField(max_length=50, verbose_name="National Insurance Number")
    
  
    position = models.CharField(
        max_length=50,
        choices=Position.choices,
        default=Position.STAFF, 
        help_text="Select the official job title."
    ) 
    
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_joined = models.DateField()
    
   
    typing_speed = models.IntegerField(
        blank=True, 
        null=True, 
        validators=[
            MinValueValidator(10, message="Typing speed must be at least 10 WPM."),
            MaxValueValidator(250, message="Typing speed cannot exceed 250 WPM.")
        ],
        help_text="Secretarial staff only (Words Per Minute)."
    )

    def clean(self):
        super().clean()
        
        # 🌟 CONDITIONAL CONSTRAINT: Enforce rules based on the position
        if self.position == self.Position.SECRETARY:
            if self.typing_speed is None:
                raise ValidationError({
                    "typing_speed": "Secretarial staff must have a recorded typing speed."
                })
        else:
            # Auto-clean data: If a non-secretary somehow gets a typing speed, clear it.
            self.typing_speed = None

    manager_start_date = models.DateField(blank=True, null=True, help_text="Managers only")
    bonus_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    car_allowance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, related_name='staff')
    
    supervisor = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subordinates',
        limit_choices_to={'position': Position.SUPERVISOR}, 
        help_text="The supervisor overseeing this staff member."
    )
    
    class Meta:
        verbose_name_plural = "Staff"
        
    def __str__(self):
        return f"{self.staff_no} - {self.first_name} {self.last_name} ({self.get_position_display()})"

    def clean(self):
        super().clean()
        
        # 🌟 ENFORCE MAX STAFF RULE
        if self.supervisor:
            current_subordinates_count = self.supervisor.subordinates.count()
            
            if not self.pk or Staff.objects.get(pk=self.pk).supervisor != self.supervisor:
                if current_subordinates_count >= 10:
                    raise ValidationError({
                        "supervisor": f"Supervisor {self.supervisor.first_name} already manages the maximum of 10 staff members."
                    })
                    
        # 🌟 BONUS RULE: Enforce role-specific fields based on the new choices
        if self.position == self.Position.MANAGER and not self.manager_start_date:
            raise ValidationError({"manager_start_date": "Managers must have a start date."})
            
        if self.position == self.Position.SECRETARY and not self.typing_speed:
            raise ValidationError({"typing_speed": "Secretarial staff must have a recorded typing speed."})


# ==========================================
# 2. UNIFIED CLIENT MODELS 
# ==========================================

class Client(models.Model): # Add CustomIDMixin here if you are using it
    
    class Role(models.TextChoices):
        RENTER = 'Renter', 'Renter'
        OWNER = 'Owner', 'Property Owner'

    # 🌟 SECURE LOGIN LINK: Required for them to log into the system
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='client_profile',
        help_text="The Django User account tied to this client for login."
        
    )
    
    # 🌟 ID & ROLE
    client_no = models.CharField(max_length=12, primary_key=True, editable=False, blank=True)
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.RENTER,
        help_text="Determines their permissions and workflows."
    )

    # 🌟 CORE CASE STUDY DETAILS
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, default='Unknown Address')
    telephone_no = models.CharField(max_length=50)
    
    # 🌟 REQUIRED FOR MODERN LOGIN
    email = models.EmailField(max_length=255, unique=True, default='placeholder@example.com')

    def __str__(self):
        return f"{self.client_no} - {self.first_name} {self.last_name} ({self.get_role_display()})"

class RenterRequirement(models.Model):
    """
    Holds the specific property requirements if the Client is a RENTER or BOTH.
    Matches the 'Property Requirement Details' from the case study form.
    """
    
    # 🌟 NEW: Define strict choices for property types
    class PropertyType(models.TextChoices):
        HOUSE = 'House', 'House'
        FLAT = 'Flat', 'Flat'

    client = models.OneToOneField(
        'Client', # Ensure this points to your Client model properly
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='renter_requirements'
    )
    
    # 🌟 UPDATED: Apply choices to the CharField
    pref_property_type = models.CharField(
        max_length=50, 
        choices=PropertyType.choices, # Creates a dropdown in forms/admin
        blank=True, 
        null=True, 
        verbose_name="Preferred Property Type",
        help_text="Select House or Flat."
    )
    
    max_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # 🌟 NEW: Added to fully match the Case Study's "General Comments" section
    general_comments = models.TextField(blank=True, null=True, verbose_name="General Comments")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(pref_property_type__in=['House', 'Flat']) | models.Q(pref_property_type__isnull=True), # 🌟 Changed 'check' to 'condition'
                name='chk_valid_property_type'
            )
        ]

    def clean(self):
        super().clean()
        # Optional Backup Validation
        if self.pref_property_type and self.pref_property_type not in self.PropertyType.values:
             raise ValidationError({"pref_property_type": "Property type must be either 'House' or 'Flat'."})

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
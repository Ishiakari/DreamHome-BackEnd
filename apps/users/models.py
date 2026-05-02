
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Options
SEX_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('P', 'Prefer not to say')
]

class Staff(models.Model):
    class Position(models.TextChoices):
        STAFF = 'Staff', 'Standard Staff'
        MANAGER = 'Manager', 'Manager'
        SUPERVISOR = 'Supervisor', 'Supervisor'
        SECRETARY = 'Secretary', 'Secretarial Staff'

    user_no = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    staff_no = models.CharField(max_length=10, primary_key=True, editable=False, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
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

    # 🌟 MERGED CLEAN METHOD
    def clean(self):
        super().clean()
        
        # Role-specific Validation
        if self.position == self.Position.SECRETARY:
            if self.typing_speed is None:
                raise ValidationError({"typing_speed": "Secretarial staff must have a recorded typing speed."})
        elif self.position == self.Position.MANAGER:
            if not self.manager_start_date:
                raise ValidationError({"manager_start_date": "Managers must have a start date."})
        else:
            # Clear fields if position changes from Manager/Secretary to something else
            self.typing_speed = None
            self.manager_start_date = None

        # Supervisor Max Capacity Rule (10 subordinates)
        if self.supervisor:
            current_subordinates_count = self.supervisor.subordinates.count()
            if not self.pk or Staff.objects.get(pk=self.pk).supervisor != self.supervisor:
                if current_subordinates_count >= 10:
                    raise ValidationError({
                        "supervisor": f"Supervisor {self.supervisor.first_name} already manages 10 staff."
                    })

    class Meta:
        verbose_name_plural = "Staff"
        
    def __str__(self):
        return f"{self.staff_no} - {self.first_name} {self.last_name} ({self.get_position_display()})"



class Client(models.Model):
    class Role(models.TextChoices):
        RENTER = 'Renter', 'Renter'
        OWNER = 'Owner', 'Property Owner'

    user_no = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='client_profile')
    client_no = models.CharField(max_length=12, primary_key=True, editable=False, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RENTER)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, default='Unknown Address')
    telephone_no = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True, default='placeholder@example.com')

    # --- NEW FIELDS BASED ON DIAGRAM ---
    
    date_registered = models.DateField(
        auto_now_add=True, 
        help_text="The date this client was registered.",
        null=True, # Allow null to handle cases where the client might be created without a registration date
    )
    
    registered_branch = models.ForeignKey(
        'branches.Branch', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='registered_clients',
        db_column='registering_branch_no' # Maps exactly to the column name in your image
    )
    
    registered_staff = models.ForeignKey(
        'users.Staff', # Assuming Staff is in your 'users' app from the previous context
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='registered_clients',
        db_column='registering_staff_no' # Maps exactly to the column name in your image
    )

    def __str__(self):
        return f"{self.client_no} - {self.first_name} {self.last_name} ({self.get_role_display()})"

class RenterRequirement(models.Model):
    class PropertyType(models.TextChoices):
        HOUSE = 'House', 'House'
        FLAT = 'Flat', 'Flat'

    client_no = models.OneToOneField(Client, on_delete=models.CASCADE, primary_key=True, related_name='renter_requirements')
    pref_property_type = models.CharField(max_length=50, choices=PropertyType.choices, blank=True, null=True)
    max_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    general_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Requirements for {self.client.first_name}"

class NextOfKin(models.Model):
    staff_no = models.OneToOneField(Staff, on_delete=models.CASCADE, primary_key=True, related_name='next_of_kin')
    full_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    telephone_no = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Next of Kin"

# 🌟 AUTOMATED CLEANUP SIGNAL
@receiver(post_delete, sender=Staff)
@receiver(post_delete, sender=Client)
def delete_related_user(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
from django.db import models

class Branch(models.Model):

    BARANGAY_CHOICES = [
        ('Carmen', 'Carmen'),
        ('Lapasan', 'Lapasan'),
        ('Macasandig', 'Macasandig'),
        ('Poblacion', 'Poblacion'),
        ('Lumbia', 'Lumbia'),
        # Add more here...
    ]

    branch_no = models.CharField(max_length=3, primary_key=True, editable=False, blank=True)
    street = models.CharField(max_length=255)
    
    # 🌟 Apply the choices here
    area = models.CharField(
        max_length=100, 
        choices=BARANGAY_CHOICES, 
        blank=True, 
        null=True,
        help_text="Select the Barangay"
    )
    
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    telephone_no = models.CharField(max_length=50)
    fax_no = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.branch_no} - {self.city}"
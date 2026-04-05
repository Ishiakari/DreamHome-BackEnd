from django.db import models

class Branch(models.Model):
    branch_no = models.CharField(
        max_length=3, 
        primary_key=True, 
        editable=False, 
        blank=True, 
        help_text="Auto-generated 3-character identifier (e.g., B01)"
    )
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    telephone_no = models.CharField(max_length=50)
    fax_no = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.branch_no} - {self.city}"
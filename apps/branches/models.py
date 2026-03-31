from django.db import models

# Create your models here.
class Branch(models.Model):
    name = models.CharField(max_length=10, primary_key=True, help_text="Unique branch identifier (e.g., B85)")
    street = models.CharField(max_length=255)
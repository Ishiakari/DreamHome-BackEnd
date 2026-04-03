from django.contrib import admin
from .models import Client, Staff  # Import your models here

# This tells Django to display the Client table
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    # This controls the columns you see in the list
    list_display = ('client_no', 'first_name', 'last_name', 'email', 'role')
    
    # This adds a search bar to find users quickly
    search_fields = ('client_no', 'email', 'last_name')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    # Change 'role' to 'position' (or whatever you named it in models.py)
    list_display = ('staff_no', 'first_name', 'last_name', 'position') 
    search_fields = ('staff_no', 'last_name')

# Register your models here.

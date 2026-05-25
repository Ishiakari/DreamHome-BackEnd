from django.contrib import admin
from .models import Payment

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_no', 'lease', 'amount_paid', 'payment_date', 'status', 'processed_by_staff')
    list_filter = ('status', 'payment_date')
    search_fields = ('payment_no', 'lease__lease_no', 'lease__renter_no__client_no')

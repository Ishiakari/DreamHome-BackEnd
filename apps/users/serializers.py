from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'  # This automatically includes all fields (first_name, email, etc.)
        
        # It tells Django: "Do not ask React for the client_no. 
        # The PostgreSQL Database Trigger will handle it."
        read_only_fields = ['client_no']
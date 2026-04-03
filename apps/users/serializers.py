from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, RenterRequirement, Staff, NextOfKin

# ==========================================
# SERIALIZERS (The Translators)
# ==========================================

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"

class RenterRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenterRequirement
        fields = "__all__"

class ClientSerializer(serializers.ModelSerializer):
    # 🌟 Added to accept the password securely from the frontend without returning it
    password = serializers.CharField(write_only=True)
    
    # Automatically includes the renter's requirements inside the JSON response
    renter_requirements = RenterRequirementSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"
        
        # 🌟 Protect both the DB-generated ID and the core User link
        read_only_fields = ['client_no', 'user']

    # 🌟 Overriding the create method to handle the Two-Table setup securely
    def create(self, validated_data):
        # 1. Safely extract the password and email from the incoming data
        password = validated_data.pop('password')
        email = validated_data.get('email')

        # 2. Create the core authentication User
        # Using create_user ensures the password is securely hashed in the database
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # 3. Create the Client profile and link it to the new auth User
        client = Client.objects.create(user=user, **validated_data)
        
        return client
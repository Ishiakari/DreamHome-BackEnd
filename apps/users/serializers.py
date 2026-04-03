from rest_framework import serializers
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
    # This automatically includes the renter's requirements inside the JSON response
    renter_requirements = RenterRequirementSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"
        
        # 🌟 THE MAGIC LINE FOR TRIGGER 🌟
        # Tells Django: "Don't ask the frontend for client_no. The DB handles it."
        read_only_fields = ['client_no']
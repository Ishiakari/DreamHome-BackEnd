from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, RenterRequirement, Staff, NextOfKin
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# ==========================================
# SERIALIZERS (The Translators)
# ==========================================

class StaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Staff
        fields = "__all__"
        read_only_fields = ['staff_no', 'user']

    def create(self, validated_data):
        password = validated_data.pop('password', 'dreamhome2026')
        email = validated_data.get('email')

        # Auto-generate staff_no
        last_staff = Staff.objects.order_by('-staff_no').first()
        if last_staff and last_staff.staff_no.startswith('S'):
            try:
                new_seq = int(last_staff.staff_no[1:]) + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1
        staff_no = f"S{new_seq:03d}"
        validated_data['staff_no'] = staff_no

        user = None
        if email:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            # Give staff access to django admin if needed, and standard staff permission
            user.is_staff = True
            user.save()

        staff = Staff.objects.create(user=user, **validated_data)
        return staff

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        instance = super().update(instance, validated_data)

        if instance.user:
            user_needs_save = False
            if 'email' in validated_data and instance.user.email != validated_data['email']:
                instance.user.email = validated_data['email']
                instance.user.username = validated_data['email']
                user_needs_save = True
            if 'first_name' in validated_data and instance.user.first_name != validated_data['first_name']:
                instance.user.first_name = validated_data['first_name']
                user_needs_save = True
            if 'last_name' in validated_data and instance.user.last_name != validated_data['last_name']:
                instance.user.last_name = validated_data['last_name']
                user_needs_save = True
            if password:
                instance.user.set_password(password)
                user_needs_save = True
                
            if user_needs_save:
                instance.user.save()

        return instance

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

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims (Data we want inside the token)
        try:
            client_profile = user.client_profile # This uses the related_name from your model
            token['role'] = client_profile.role
            token['first_name'] = client_profile.first_name
        except:
            token['role'] = 'ADMIN' # For superusers/staff

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
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

    # 🌟 SECURE VALIDATION: Catch duplicates before the database crashes!
    def validate_email(self, value):
        # If this is an UPDATE and they kept their current email, let it pass.
        if self.instance and self.instance.email == value:
            return value
        
        # If it's a NEW email, check if any User already has it.
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value

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
    # Keep their password and renter_requirements settings
    password = serializers.CharField(write_only=True, required=False)
    renter_requirements = RenterRequirementSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ['client_no', 'user']

    # Keep their existing secure email validation
    def validate_email(self, value):
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value

    # Keep their existing create method
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        client = Client.objects.create(user=user, **validated_data)
        return client

    # 🌟 ADD THIS: This is the new part that matches the Staff logic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Update Client fields (telephone_no, address, etc.)
        instance = super().update(instance, validated_data)

        # Sync with the User login table
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

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        try:
            client_profile = user.client_profile
            token['role'] = client_profile.role
            token['first_name'] = client_profile.first_name
        except:
            token['role'] = 'ADMIN'

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
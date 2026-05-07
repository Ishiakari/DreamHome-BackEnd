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
        read_only_fields = ['staff_no', 'user_no']  # FIX

    # validate_email unchanged

    def create(self, validated_data):
        password = validated_data.pop('password', 'dreamhome2026')
        email = validated_data.get('email')

        # generate staff_no unchanged...

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

        staff = Staff.objects.create(user_no=user, **validated_data)  # FIX
        return staff

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        instance = super().update(instance, validated_data)

        if instance.user_no:  # FIX
            user_needs_save = False
            if 'email' in validated_data and instance.user_no.email != validated_data['email']:
                instance.user_no.email = validated_data['email']
                instance.user_no.username = validated_data['email']
                user_needs_save = True
            if 'first_name' in validated_data and instance.user_no.first_name != validated_data['first_name']:
                instance.user_no.first_name = validated_data['first_name']
                user_needs_save = True
            if 'last_name' in validated_data and instance.user_no.last_name != validated_data['last_name']:
                instance.user_no.last_name = validated_data['last_name']
                user_needs_save = True
            if password:
                instance.user_no.set_password(password)
                user_needs_save = True

            if user_needs_save:
                instance.user_no.save()

        return instance


class RenterRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenterRequirement
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    renter_requirements = RenterRequirementSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ['client_no', 'user_no']  # FIX

    # validate_email unchanged

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
        client = Client.objects.create(user_no=user, **validated_data)  # FIX
        return client

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        instance = super().update(instance, validated_data)

        if instance.user_no:  # FIX
            user_needs_save = False
            if 'email' in validated_data and instance.user_no.email != validated_data['email']:
                instance.user_no.email = validated_data['email']
                instance.user_no.username = validated_data['email']
                user_needs_save = True
            if 'first_name' in validated_data and instance.user_no.first_name != validated_data['first_name']:
                instance.user_no.first_name = validated_data['first_name']
                user_needs_save = True
            if 'last_name' in validated_data and instance.user_no.last_name != validated_data['last_name']:
                instance.user_no.last_name = validated_data['last_name']
                user_needs_save = True
            if password:
                instance.user_no.set_password(password)
                user_needs_save = True

            if user_needs_save:
                instance.user_no.save()

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
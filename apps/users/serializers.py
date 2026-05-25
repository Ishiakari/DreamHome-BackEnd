from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Client, RenterRequirement, Staff, NextOfKin, HiringApplication


class NextOfKinSerializer(serializers.ModelSerializer):
    suffix = serializers.CharField(source="suffixes", required=False, allow_blank=True)

    class Meta:
        model = NextOfKin
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "suffix",
            "relationship",
            "address",
            "telephone_no"
        ]
        extra_kwargs = {
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "middle_name": {"required": False, "allow_blank": True},
            "relationship": {"required": False, "allow_blank": True},
            "address": {"required": False, "allow_blank": True},
            "telephone_no": {"required": False, "allow_blank": True}
        }


class StaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    next_of_kin = NextOfKinSerializer(required=False, allow_null=True)

    class Meta:
        model = Staff
        fields = "__all__"
        read_only_fields = ["staff_no", "user_no"]

    def _save_next_of_kin(self, staff, next_of_kin_data):
        if not next_of_kin_data:
            return

        cleaned = {
            key: value
            for key, value in next_of_kin_data.items()
            if value not in (None, "")
        }

        if not cleaned:
            return

        NextOfKin.objects.update_or_create(
            staff_no=staff,
            defaults=cleaned
        )

    def validate_email(self, value):
        # If this is an UPDATE and they kept their current email, let it pass.
        if self.instance and self.instance.email == value:
            return value

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value

    def create(self, validated_data):
        next_of_kin_data = validated_data.pop("next_of_kin", None)
        password = validated_data.pop("password", "dreamhome2026")
        email = validated_data.get("email")

        # Auto-generate staff_no
        last_staff = Staff.objects.order_by("-staff_no").first()
        if last_staff and last_staff.staff_no and last_staff.staff_no.startswith("S"):
            try:
                new_seq = int(last_staff.staff_no[1:]) + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1

        validated_data["staff_no"] = f"S{new_seq:03d}"

        user = None
        if email:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
            )
            user.is_staff = True
            user.save()

        staff = Staff.objects.create(user_no=user, **validated_data)
        self._save_next_of_kin(staff, next_of_kin_data)
        return staff

    def update(self, instance, validated_data):
        next_of_kin_data = validated_data.pop("next_of_kin", None)
        password = validated_data.pop("password", None)

        instance = super().update(instance, validated_data)

        if instance.user_no:
            user_needs_save = False

            if "email" in validated_data and instance.user_no.email != validated_data["email"]:
                instance.user_no.email = validated_data["email"]
                instance.user_no.username = validated_data["email"]
                user_needs_save = True

            if "first_name" in validated_data and instance.user_no.first_name != validated_data["first_name"]:
                instance.user_no.first_name = validated_data["first_name"]
                user_needs_save = True

            if "last_name" in validated_data and instance.user_no.last_name != validated_data["last_name"]:
                instance.user_no.last_name = validated_data["last_name"]
                user_needs_save = True

            if password:
                instance.user_no.set_password(password)
                user_needs_save = True

            if user_needs_save:
                instance.user_no.save()

        self._save_next_of_kin(instance, next_of_kin_data)

        return instance


class HiringApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringApplication
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class RenterRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenterRequirement
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    renter_requirements = RenterRequirementSerializer(required=False, allow_null=True)

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ["client_no", "user_no"]

    def validate_email(self, value):
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value

    def validate_role(self, value):
        """
        Normalize and strictly validate role so we never store 'RENTER'/'OWNER' again.
        Stored DB values (TextChoices) are: 'Renter' and 'Owner'.
        """
        if value is None or str(value).strip() == "":
            return Client.Role.RENTER

        v = str(value).strip().lower()
        if v == "renter":
            return Client.Role.RENTER
        if v == "owner":
            return Client.Role.OWNER

        raise serializers.ValidationError("Role must be Renter or Owner.")

    def create(self, validated_data):
        # Normalize role (also triggers validate_role)
        role = validated_data.get("role", Client.Role.RENTER)
        validated_data["role"] = self.validate_role(role)

        # Generate client_no: CR### (Renter) or CO### (Owner)
        prefix = "CO" if validated_data["role"] == Client.Role.OWNER else "CR"

        last_client = (
            Client.objects.filter(client_no__startswith=prefix)
            .order_by("-client_no")
            .first()
        )

        if last_client and last_client.client_no and last_client.client_no.startswith(prefix):
            try:
                new_seq = int(last_client.client_no[len(prefix):]) + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1

        validated_data["client_no"] = f"{prefix}{new_seq:03d}"

        # Create Django auth user
        password = validated_data.pop("password")
        email = validated_data.get("email")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        client = Client.objects.create(user_no=user, **validated_data)
        return client

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        req_data = validated_data.pop("renter_requirements", None)

        # Normalize role on update too (optional but keeps data consistent)
        if "role" in validated_data:
            validated_data["role"] = self.validate_role(validated_data["role"])

        instance = super().update(instance, validated_data)

        # Sync Renter Requirements
        if req_data is not None and instance.role == Client.Role.RENTER:
            RenterRequirement.objects.update_or_create(
                client_no=instance,
                defaults=req_data
            )

        # Sync with Django auth User
        if instance.user_no:
            user_needs_save = False

            if "email" in validated_data and instance.user_no.email != validated_data["email"]:
                instance.user_no.email = validated_data["email"]
                instance.user_no.username = validated_data["email"]
                user_needs_save = True

            if "first_name" in validated_data and instance.user_no.first_name != validated_data["first_name"]:
                instance.user_no.first_name = validated_data["first_name"]
                user_needs_save = True

            if "last_name" in validated_data and instance.user_no.last_name != validated_data["last_name"]:
                instance.user_no.last_name = validated_data["last_name"]
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
 
        # Client (Renter or Owner)
        try:
            client_profile = user.client_profile
            token["role"] = client_profile.role          # "Renter" or "Owner"
            token["first_name"] = client_profile.first_name
            return token
        except Exception:
            pass
 
        # Staff (Manager, Supervisor, Secretary, Staff)
        try:
            staff_profile = user.staff_profile
            token["first_name"] = staff_profile.first_name
            # Superuser = ADMIN, everyone else = their actual position
            if user.is_superuser:
                token["role"] = "ADMIN"
            else:
                token["role"] = staff_profile.position  # e.g. "Manager", "Staff", "Supervisor", "Secretary"
            return token
        except Exception:
            pass
 
        # Fallback for bare superusers with no staff/client profile
        token["role"] = "ADMIN"
        token["first_name"] = user.first_name or user.username
        return token
 
 
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
 
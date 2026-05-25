from rest_framework import generics, permissions, status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny

from datetime import date
from django.db import transaction
from django.db.models.deletion import ProtectedError
from .models import Client, Staff, HiringApplication
from .serializers import ClientSerializer, StaffSerializer, HiringApplicationSerializer, HiringApplicationPublicSerializer, MyTokenObtainPairSerializer


# ============================================================
# PERMISSION CLASSES
# ============================================================

class IsAdminRole(BasePermission):
    """Only superusers (ADMIN role) can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsStaffOrAdmin(BasePermission):
    """Any logged-in staff member or superuser can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff
        )


class IsManagerOrAdmin(BasePermission):
    """Only Managers, Supervisors, and Admins can access."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            position = request.user.staff_profile.position
            return position in ["Manager", "Supervisor"]
        except Exception:
            return False


class ReadOnlyOrManagerAdmin(BasePermission):
    """GET is allowed for any staff. Write (POST/PUT/DELETE) requires Manager or Admin."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff or request.user.is_superuser
        # Write operations
        if request.user.is_superuser:
            return True
        try:
            position = request.user.staff_profile.position
            return position in ["Manager", "Supervisor"]
        except Exception:
            return False


# ============================================================
# VIEWS
# ============================================================

@api_view(["GET"])
def users_api_root(request):
    return Response({
        "staff": "/api/users/staff/",
        "clients": "/api/users/clients/",
        "signup": "/api/users/signup/",
        "hiring_applications": "/api/users/hiring-applications/",
        "hiring_tracking": "/api/users/hiring-applications/track/",
    })


# --- STAFF VIEWS ---
# Admin only: full CRUD on staff
class StaffListCreateView(generics.ListCreateAPIView):
    queryset = Staff.objects.select_related("branch", "supervisor", "next_of_kin").all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdminRole]          # ✅ Only ADMIN can create/list staff


class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Staff.objects.select_related("branch", "supervisor", "next_of_kin").all()
    serializer_class = StaffSerializer
    lookup_field = "staff_no"
    permission_classes = [IsAdminRole]          # ✅ Only ADMIN can edit/delete staff

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            related_objects_str = ", ".join([str(obj) for obj in e.protected_objects])
            return Response(
                {"detail": f"Cannot delete staff account: It is linked to active records ({related_objects_str}). Please reassign or delete those records first."},
                status=status.HTTP_400_BAD_REQUEST
            )


# --- CLIENT VIEWS ---
# Managers + Admins: full CRUD. Regular staff: read-only. Unauthenticated can POST (Sign Up).
class ClientListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [ReadOnlyOrManagerAdmin()]

    def get_queryset(self):
        queryset = Client.objects.all()
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role.capitalize())
        return queryset


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = "client_no"
    permission_classes = [ReadOnlyOrManagerAdmin]  # ✅ Staff can view, Manager/Admin can edit

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            related_objects_str = ", ".join([str(obj) for obj in e.protected_objects])
            return Response(
                {"detail": f"Cannot delete account: It is linked to active records ({related_objects_str}). Please remove or update these records first."},
                status=status.HTTP_400_BAD_REQUEST
            )


class PublicClientSignupView(generics.CreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Prevent public signups from assigning internal registration fields.
        serializer.save(registered_branch=None, registered_staff=None)


# --- HIRING APPLICATIONS ---
class HiringApplicationListCreateView(generics.ListCreateAPIView):
    queryset = HiringApplication.objects.select_related(
        "branch",
        "assigned_manager",
        "reviewed_by"
    ).all()
    serializer_class = HiringApplicationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsStaffOrAdmin()]

    def perform_create(self, serializer):
        # Public submissions must start at Applied with no internal assignments.
        if not self.request.user.is_authenticated:
            serializer.save(
                stage=HiringApplication.Stage.APPLIED,
                assigned_manager=None,
                reviewed_by=None
            )
            return
        serializer.save()


class HiringApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HiringApplication.objects.select_related(
        "branch",
        "assigned_manager",
        "reviewed_by"
    ).all()
    serializer_class = HiringApplicationSerializer
    permission_classes = [ReadOnlyOrManagerAdmin]

    def _build_next_of_kin(self, application):
        payload = {
            "first_name": application.nok_first_name,
            "last_name": application.nok_last_name,
            "middle_name": application.nok_middle_name,
            "suffix": application.nok_suffixes,
            "relationship": application.nok_relationship,
            "address": application.nok_address,
            "telephone_no": application.nok_telephone_no,
        }
        cleaned = {key: value for key, value in payload.items() if value not in (None, "")}
        return cleaned or None

    def _create_staff_from_application(self, application):
        if Staff.objects.filter(email=application.email).exists():
            return

        next_of_kin = self._build_next_of_kin(application)

        staff_payload = {
            "email": application.email,
            "first_name": application.first_name,
            "last_name": application.last_name,
            "middle_name": application.middle_name,
            "suffixes": application.suffixes,
            "address": application.address,
            "telephone_no": application.telephone_no,
            "sex": application.sex,
            "dob": application.dob,
            "nin": application.nin,
            "position": application.position,
            "salary": 30000 if application.position == Staff.Position.MANAGER else 0,
            "date_joined": application.preferred_start_date,
            "branch": application.branch.branch_no,
            "typing_speed": application.typing_speed if application.position == Staff.Position.SECRETARY else None,
            "manager_start_date": application.preferred_start_date if application.position == Staff.Position.MANAGER else None,
            "bonus_payment": None,
            "car_allowance": None,
            "supervisor": None,
        }

        if next_of_kin:
            staff_payload["next_of_kin"] = next_of_kin

        serializer = StaffSerializer(data=staff_payload)
        serializer.is_valid(raise_exception=True)
        serializer.save(password="Dreamhome101")

    def perform_update(self, serializer):
        instance = self.get_object()
        previous_stage = instance.stage

        with transaction.atomic():
            updated = serializer.save()

            staff_profile = getattr(self.request.user, "staff_profile", None)
            if staff_profile and not updated.reviewed_by:
                updated.reviewed_by = staff_profile
                updated.save(update_fields=["reviewed_by"])

            if previous_stage != HiringApplication.Stage.HIRED and updated.stage == HiringApplication.Stage.HIRED:
                if not updated.hired_date:
                    updated.hired_date = date.today()
                    updated.save(update_fields=["hired_date"])

                try:
                    self._create_staff_from_application(updated)
                except serializers.ValidationError as error:
                    raise serializers.ValidationError(error.detail)


class PublicHiringTrackingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        nin = request.data.get("nin")
        dob = request.data.get("dob")

        if not email or not nin or not dob:
            return Response(
                {"detail": "Email, National Insurance Number, and Date of Birth are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        applications = HiringApplication.objects.filter(
            email__iexact=email,
            nin=nin,
            dob=dob
        ).order_by("-created_at")

        serializer = HiringApplicationPublicSerializer(applications, many=True)
        return Response(serializer.data)


# --- CURRENT USER (PROFILE) ---
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        data = {
            "fullName": f"{user.first_name} {user.last_name}".strip() or user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "role": "ADMIN" if user.is_superuser else "STAFF",
        }

        if hasattr(user, "client_profile"):
            client = user.client_profile
            data.update({
                "client_no": client.client_no,
                "role": client.role,
                "telephoneNo": client.telephone_no,
                "address": client.address,
            })
            
            # Include Renter Requirements if they exist
            if client.role == Client.Role.RENTER and hasattr(client, 'renter_requirements'):
                from .serializers import RenterRequirementSerializer
                data["renter_requirements"] = RenterRequirementSerializer(client.renter_requirements).data

        elif hasattr(user, "staff_profile"):
            staff = user.staff_profile
            data.update({
                "staff_no": staff.staff_no,
                # ✅ Return actual position, not generic "STAFF"
                "role": "ADMIN" if user.is_superuser else staff.position,
                "telephoneNo": staff.telephone_no,
                "address": staff.address,
                "branchCode": staff.branch.branch_no if staff.branch else "HQ",
            })

        return Response({"user": data})

    def put(self, request):
        user = request.user

        if hasattr(user, "client_profile"):
            serializer = ClientSerializer(user.client_profile, data=request.data, partial=True)
        elif hasattr(user, "staff_profile"):
            serializer = StaffSerializer(user.staff_profile, data=request.data, partial=True)
        else:
            return Response({"error": "No profile found."}, status=404)

        if serializer.is_valid():
            serializer.save()
            refresh = MyTokenObtainPairSerializer.get_token(user)
            return Response({
                "message": "Profile updated!",
                "user": serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            })

        return Response(serializer.errors, status=400)
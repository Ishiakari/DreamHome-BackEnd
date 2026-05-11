from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny

from .models import Client, Staff
from .serializers import ClientSerializer, StaffSerializer, MyTokenObtainPairSerializer


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
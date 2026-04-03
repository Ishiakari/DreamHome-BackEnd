from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Client, Staff
from .serializers import ClientSerializer, StaffSerializer 
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# ==========================================
# VIEWS (The Doorways)
# ==========================================

@api_view(["GET"])
def users_api_root(request):
    return Response(
        {
            "staff": "/api/users/staff/",
            "clients": "/api/users/clients/", # Replaced renters/owners with unified endpoint
        }
    )

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow Staff/Admin roles.
    """
    def has_permission(self, request, view):
        # Check if the user is logged in AND has the correct role
        return request.user.is_authenticated and (
            request.user.is_staff or 
            getattr(request.user, 'role', None) == 'STAFF'
        )


class StaffListView(generics.ListAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    # 🛡️ ONLY the Admin Repo (using a Staff account) can see this!
    permission_classes = [IsAdminUser]

# --- STAFF VIEWS ---

class StaffListCreateView(generics.ListCreateAPIView):
    queryset = Staff.objects.select_related("branch", "supervisor").all()
    serializer_class = StaffSerializer

class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Staff.objects.select_related("branch", "supervisor").all()
    serializer_class = StaffSerializer
    lookup_field = "staff_no"


# --- CLIENT VIEWS (Handles both Renters and Owners) ---

class ClientListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer

    def get_queryset(self):
        """
        This allows the frontend to easily filter by role.
        Example: /api/users/clients/?role=RENTER
        """
        queryset = Client.objects.all()
        role = self.request.query_params.get('role')
        if role:
            # Filters the database before sending the JSON back
            queryset = queryset.filter(role=role.upper())
        return queryset

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = "client_no"


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = "ADMIN" if user.is_superuser else "STAFF"
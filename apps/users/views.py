from rest_framework import generics, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    # This automatically includes the renter's requirements inside the JSON response if they exist!
    renter_requirements = RenterRequirementSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"


# ==========================================
# VIEWS (The Doorways)
# ==========================================

@api_view(["GET"])
def users_api_root(request):
    return Response(
        {
            "staff": "/api/users/staff/",
            "clients": "/api/users/clients/", # Replaced renters/owners with the unified endpoint
        }
    )

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
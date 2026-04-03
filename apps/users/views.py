from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Client, Staff
from .serializers import ClientSerializer, StaffSerializer 

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
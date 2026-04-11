from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Client, Staff
from .serializers import ClientSerializer, StaffSerializer, MyTokenObtainPairSerializer

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
        
        # Basic data that everyone has
        data = {
            "fullName": f"{user.first_name} {user.last_name}".strip() or user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "role": "ADMIN" if user.is_superuser else "STAFF",
        }

        # 🌟 Improved logic: Adds ALL fields from the Client model
        if hasattr(user, 'client_profile'):
            client = user.client_profile
            data.update({
                "client_no": client.client_no,
                "role": client.role,
                "telephoneNo": client.telephone_no,
                "address": client.address
            })

        elif hasattr(user, 'staff_profile'):
            staff = user.staff_profile
            data.update({
                "staff_no": staff.staff_no,
                "role": "STAFF",
                "telephoneNo": staff.telephone_no,
                "address": staff.address,
                "branchCode": staff.branch.branch_no if staff.branch else "HQ"
            })

        return Response({"user": data})

    # 🌟 NEW: Handles the actual "Save" click from Next.js
    def put(self, request):
        user = request.user
        
        if hasattr(user, 'client_profile'):
            serializer = ClientSerializer(user.client_profile, data=request.data, partial=True)
        elif hasattr(user, 'staff_profile'):
            serializer = StaffSerializer(user.staff_profile, data=request.data, partial=True)
        else:
            return Response({"error": "No profile found."}, status=404)

        if serializer.is_valid():
            serializer.save()
            
            # 🌟 THE FINAL BOSS FIX: Generate fresh tokens with the NEW data baked in!
            refresh = MyTokenObtainPairSerializer.get_token(user)
            
            return Response({
                "message": "Profile updated!", 
                "user": serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            })
        
        return Response(serializer.errors, status=400)
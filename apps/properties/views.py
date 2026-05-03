from rest_framework import generics, serializers, permissions
# apps/properties/views.py
from .models import Advertisement, Property, PropertyInspection, PropertyViewing
from apps.users.models import Client

# ✅ add this import (we created this file already)
from .permissions import ReadOnlyOrAuthenticated

# --- SERIALIZERS ---

class PropertyForRentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"
        # owner is read-only because we set it automatically in the View
        read_only_fields = ["owner"]


class PropertyViewingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyViewing
        fields = "__all__"


class PropertyInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInspection
        fields = "__all__"


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = "__all__"


# --- HELPERS ---

def get_client_profile_or_error(user):
    try:
        return Client.objects.get(user=user)
    except Client.DoesNotExist:
        raise serializers.ValidationError(
            {
                "detail": "Your user account is not linked to a Client profile. "
                        "Create a Client record for this user in the Admin panel."
            }
        )


# --- VIEWS ---

class PropertyForRentListCreateView(generics.ListCreateAPIView):
    """
    Public READ (GET), authenticated WRITE (POST).
    """
    queryset = Property.objects.select_related("owner_no", "staff_no", "branch_no").all()
    serializer_class = PropertyForRentSerializer
    permission_classes = [ReadOnlyOrAuthenticated]  # ✅ changed

    def perform_create(self, serializer):
        # Assign owner based on logged in user's Client profile
        client_profile = get_client_profile_or_error(self.request.user)
        serializer.save(owner=client_profile)


class MyPropertyForRentListView(generics.ListAPIView):
    """
    'My Listings' (owner-only view).
    """
    serializer_class = PropertyForRentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        base_qs = Property.objects.select_related("owner_no", "staff_no", "branch_no")

        client_profile = get_client_profile_or_error(self.request.user)

        # Optional: enforce role if you want
        if getattr(client_profile, "role", None) != "Owner":
            return base_qs.none()

        return base_qs.filter(owner=client_profile)


class PropertyForRentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.select_related("owner_no", "staff_no", "branch_no").all()
    serializer_class = PropertyForRentSerializer
    lookup_field = "property_no"
    permission_classes = [permissions.IsAuthenticated]


class PropertyViewingListCreateView(generics.ListCreateAPIView):
    queryset = PropertyViewing.objects.select_related("property", "renter").all()
    serializer_class = PropertyViewingSerializer
    permission_classes = [permissions.IsAuthenticated]


class PropertyViewingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyViewing.objects.select_related("property", "renter").all()
    serializer_class = PropertyViewingSerializer
    permission_classes = [permissions.IsAuthenticated]


class PropertyInspectionListCreateView(generics.ListCreateAPIView):
    queryset = PropertyInspection.objects.select_related("property", "staff").all()
    serializer_class = PropertyInspectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class PropertyInspectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyInspection.objects.select_related("property", "staff").all()
    serializer_class = PropertyInspectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdvertisementListCreateView(generics.ListCreateAPIView):
    queryset = Advertisement.objects.select_related("property").all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdvertisementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Advertisement.objects.select_related("property").all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]
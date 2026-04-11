from rest_framework import generics, serializers, permissions
from .models import Advertisement, PropertyForRent, PropertyInspection, PropertyViewing
# 🌟 IMPORTANT: Change 'apps.users.models' if your Client model is elsewhere!
from apps.users.models import Client 

# --- SERIALIZERS ---

class PropertyForRentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyForRent
        fields = "__all__"
        # 🌟 'owner' is read-only because we set it automatically in the View
        read_only_fields = ['owner']

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


# --- VIEWS ---

class PropertyForRentListCreateView(generics.ListCreateAPIView):
    queryset = PropertyForRent.objects.select_related("owner", "staff", "branch").all()
    serializer_class = PropertyForRentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 🌟 THE FIX:
        # We find the 'Client' profile that belongs to the logged-in user.
        try:
            client_profile = Client.objects.get(user=self.request.user)
            serializer.save(owner=client_profile)
        except Client.DoesNotExist:
            # This handles the case where you are logged in but don't have a Client profile
            raise serializers.ValidationError({
                "detail": "Your user account is not linked to a Client profile. Please check the Admin panel."
            })


class PropertyForRentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyForRent.objects.select_related("owner", "staff", "branch").all()
    serializer_class = PropertyForRentSerializer
    lookup_field = "property_no"


class PropertyViewingListCreateView(generics.ListCreateAPIView):
    queryset = PropertyViewing.objects.select_related("property", "renter").all()
    serializer_class = PropertyViewingSerializer


class PropertyViewingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyViewing.objects.select_related("property", "renter").all()
    serializer_class = PropertyViewingSerializer


class PropertyInspectionListCreateView(generics.ListCreateAPIView):
    queryset = PropertyInspection.objects.select_related("property", "staff").all()
    serializer_class = PropertyInspectionSerializer


class PropertyInspectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyInspection.objects.select_related("property", "staff").all()
    serializer_class = PropertyInspectionSerializer


class AdvertisementListCreateView(generics.ListCreateAPIView):
    queryset = Advertisement.objects.select_related("property").all()
    serializer_class = AdvertisementSerializer


class AdvertisementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Advertisement.objects.select_related("property").all()
    serializer_class = AdvertisementSerializer
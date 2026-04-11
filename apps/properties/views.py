from rest_framework import generics, serializers, permissions
from .models import Advertisement, PropertyForRent, PropertyInspection, PropertyViewing

# --- SERIALIZERS ---

class PropertyForRentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyForRent
        fields = "__all__"
        # 🌟 Make owner read-only so the API doesn't require it in the form
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
    # 🌟 Ensure the user is logged in
    permission_classes = [permissions.IsAuthenticated]

    # 🌟 THIS IS THE FIX:
    def perform_create(self, serializer):
        # Automatically set the owner to the current logged-in user
        serializer.save(owner=self.request.user)


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
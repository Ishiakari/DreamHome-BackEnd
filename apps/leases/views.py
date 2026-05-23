from rest_framework import generics, serializers
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import LeaseAgreement


class IsManagerOrAdmin(BasePermission):
    """Only Managers, Supervisors, and Admins can write leases. All staff can read."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.is_staff or request.user.is_superuser
        if request.user.is_superuser:
            return True
        try:
            position = request.user.staff_profile.position
            return position in ["Manager", "Supervisor"]
        except Exception:
            return False


class LeaseAgreementSerializer(serializers.ModelSerializer):
    # Overriding property_no to bypass model's limit_choices_to={'status': 'Available'} 
    # which prevents editing leases once the property status changes to 'Rented'.
    from apps.properties.models import Property
    property_no = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = LeaseAgreement
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Inject nested data for better frontend display
        # Note: We import here to avoid potential circular dependencies
        from apps.properties.views import PropertyForRentSerializer
        from apps.users.serializers import ClientSerializer
        
        if instance.property_no:
            representation['property_no'] = PropertyForRentSerializer(instance.property_no).data
        if instance.renter_no:
            representation['renter_no'] = ClientSerializer(instance.renter_no).data
            
        return representation

    def validate(self, data):
        # Enforce that a lease can only be created if there is an accepted PropertyViewing
        # for this specific property and renter.
        property_obj = data.get('property_no', getattr(self.instance, 'property_no', None))
        renter_obj = data.get('renter_no', getattr(self.instance, 'renter_no', None))

        # Check if it's a new lease or if the property/renter is being changed
        is_new = self.instance is None
        property_changed = is_new or ('property_no' in data and getattr(self.instance, 'property_no', None) != property_obj)
        renter_changed = is_new or ('renter_no' in data and getattr(self.instance, 'renter_no', None) != renter_obj)

        if (property_changed or renter_changed) and property_obj and renter_obj:
            from apps.properties.models import PropertyViewing
            
            # Check if there's any approved viewing for this renter and property
            has_approved_viewing = PropertyViewing.objects.filter(
                property_no=property_obj,
                renter_no=renter_obj,
                status='Approved'
            ).exists()
            
            if not has_approved_viewing:
                raise serializers.ValidationError(
                    "Cannot create or update this lease: The renter must have an 'Approved' property viewing for this property."
                )

        return data


class LeaseAgreementListCreateView(generics.ListCreateAPIView):
    queryset = LeaseAgreement.objects.select_related("renter_no", "property_no", "staff_no").all()
    serializer_class = LeaseAgreementSerializer
    permission_classes = [IsManagerOrAdmin]


class LeaseAgreementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaseAgreement.objects.select_related("renter_no", "property_no", "staff_no").all()
    serializer_class = LeaseAgreementSerializer
    lookup_field = "lease_no"
    permission_classes = [IsManagerOrAdmin]
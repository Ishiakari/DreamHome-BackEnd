from rest_framework import generics, serializers, permissions
from .models import Payment
from apps.leases.models import LeaseAgreement
from apps.users.models import Staff

# --- SERIALIZER ---

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["payment_no", "status", "processed_by_staff"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Inject nested lease data for the frontend banner and table
        from apps.leases.views import LeaseAgreementSerializer
        if instance.lease:
            representation['lease'] = LeaseAgreementSerializer(instance.lease).data
            
        return representation

# --- VIEWS ---

class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related("lease", "processed_by_staff").all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Auto-assign the staff member who logged the payment
        staff_profile = getattr(self.request.user, "staff_profile", None)
        serializer.save(
            processed_by_staff=staff_profile,
            status=Payment.PaymentStatus.COMPLETED # Auto-complete on creation
        )


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.select_related("lease", "processed_by_staff").all()
    serializer_class = PaymentSerializer
    lookup_field = "payment_no"
    permission_classes = [permissions.IsAuthenticated]

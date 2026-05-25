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

    def create(self, validated_data):
        existing_ids = Payment.objects.filter(payment_no__startswith="PAY").values_list("payment_no", flat=True)
        max_seq = 0
        for pid in existing_ids:
            try:
                num = int(pid[3:])
                if num > max_seq:
                    max_seq = num
            except ValueError:
                pass
        
        validated_data["payment_no"] = f"PAY{max_seq + 1:03d}"
        return super().create(validated_data)

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

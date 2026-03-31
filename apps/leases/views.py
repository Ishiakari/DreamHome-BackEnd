from rest_framework import generics, serializers

from .models import LeaseAgreement


class LeaseAgreementSerializer(serializers.ModelSerializer):
	class Meta:
		model = LeaseAgreement
		fields = "__all__"


class LeaseAgreementListCreateView(generics.ListCreateAPIView):
	queryset = LeaseAgreement.objects.select_related("renter", "property", "staff").all()
	serializer_class = LeaseAgreementSerializer


class LeaseAgreementDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = LeaseAgreement.objects.select_related("renter", "property", "staff").all()
	serializer_class = LeaseAgreementSerializer
	lookup_field = "lease_no"

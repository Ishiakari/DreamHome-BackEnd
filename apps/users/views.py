from rest_framework import generics, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PropertyOwner, Renter, Staff


class StaffSerializer(serializers.ModelSerializer):
	class Meta:
		model = Staff
		fields = "__all__"


class RenterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Renter
		fields = "__all__"


class PropertyOwnerSerializer(serializers.ModelSerializer):
	class Meta:
		model = PropertyOwner
		fields = "__all__"


@api_view(["GET"])
def users_api_root(request):
	return Response(
		{
			"staff": "/api/users/staff/",
			"renters": "/api/users/renters/",
			"owners": "/api/users/owners/",
		}
	)


class StaffListCreateView(generics.ListCreateAPIView):
	queryset = Staff.objects.select_related("branch", "supervisor").all()
	serializer_class = StaffSerializer


class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Staff.objects.select_related("branch", "supervisor").all()
	serializer_class = StaffSerializer
	lookup_field = "staff_no"


class RenterListCreateView(generics.ListCreateAPIView):
	queryset = Renter.objects.all()
	serializer_class = RenterSerializer


class RenterDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Renter.objects.all()
	serializer_class = RenterSerializer
	lookup_field = "renter_no"


class PropertyOwnerListCreateView(generics.ListCreateAPIView):
	queryset = PropertyOwner.objects.all()
	serializer_class = PropertyOwnerSerializer


class PropertyOwnerDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PropertyOwner.objects.all()
	serializer_class = PropertyOwnerSerializer
	lookup_field = "owner_no"

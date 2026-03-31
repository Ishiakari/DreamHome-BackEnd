from rest_framework import generics, serializers

from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
	class Meta:
		model = Branch
		fields = "__all__"


class BranchListCreateView(generics.ListCreateAPIView):
	queryset = Branch.objects.all()
	serializer_class = BranchSerializer


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Branch.objects.all()
	serializer_class = BranchSerializer
	lookup_field = "name"

from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission
from .models import Branch

class ReadOnlyOrAuthenticated(BasePermission):
    """Allow unauthenticated read-only access; require authentication for writes."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"

class BranchListCreateView(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [ReadOnlyOrAuthenticated]

class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    lookup_field = "branch_no"
    permission_classes = [IsAuthenticated]
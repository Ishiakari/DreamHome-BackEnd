from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from .models import Branch
 
 
class IsAdminRole(BasePermission):
    """Only superusers can write. Anyone can read (public frontend)."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Anyone can view
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser  # Only ADMIN can POST/PUT/DELETE
 
 
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
 
 
class BranchListCreateView(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminRole]   # ✅ All staff can view, only ADMIN can create
 
 
class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    lookup_field = "branch_no"
    permission_classes = [IsAdminRole]   # ✅ All staff can view, only ADMIN can edit/delete
 
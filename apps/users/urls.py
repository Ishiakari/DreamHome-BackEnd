from django.urls import path
from . import views

urlpatterns = [
    # API Root
    path("", views.users_api_root, name="users-api-root"),
    
    # Staff URLs
    path("staff/", views.StaffListCreateView.as_view(), name="staff-list-create"),
    path("staff/<str:staff_no>/", views.StaffDetailView.as_view(), name="staff-detail"),
    
    # 🌟 Unified Client URLs (Handles both Renters and Owners)
    path("clients/", views.ClientListCreateView.as_view(), name="client-list-create"),
    path("clients/<str:client_no>/", views.ClientDetailView.as_view(), name="client-detail"),
]
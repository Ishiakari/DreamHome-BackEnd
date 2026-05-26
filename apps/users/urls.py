from django.urls import path
from . import views

urlpatterns = [
    # API Root
    path("", views.users_api_root, name="users-api-root"),
    
    # Current User (Profile)
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    
    # Staff URLs
    path("staff/", views.StaffListCreateView.as_view(), name="staff-list-create"),
    path("staff/performance-report/", views.StaffPerformanceReportView.as_view(), name="staff-performance-report"),
    path("staff/<str:staff_no>/", views.StaffDetailView.as_view(), name="staff-detail"),
    
    # 🌟 Unified Client URLs (Handles both Renters and Owners)
    path("clients/", views.ClientListCreateView.as_view(), name="client-list-create"),
    path("clients/<str:client_no>/", views.ClientDetailView.as_view(), name="client-detail"),

    # Public Signup (Web Registrations)
    path("signup/", views.PublicClientSignupView.as_view(), name="public-client-signup"),

    # Hiring Applications
    path("hiring-applications/", views.HiringApplicationListCreateView.as_view(), name="hiring-application-list-create"),
    path("hiring-applications/<int:pk>/", views.HiringApplicationDetailView.as_view(), name="hiring-application-detail"),
    path("hiring-applications/track/", views.PublicHiringTrackingView.as_view(), name="hiring-application-track"),
]
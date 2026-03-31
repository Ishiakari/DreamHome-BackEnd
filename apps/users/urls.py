from django.urls import path

from . import views

urlpatterns = [
    path("", views.users_api_root, name="users-api-root"),
    path("staff/", views.StaffListCreateView.as_view(), name="staff-list-create"),
    path("staff/<str:staff_no>/", views.StaffDetailView.as_view(), name="staff-detail"),
    path("renters/", views.RenterListCreateView.as_view(), name="renter-list-create"),
    path("renters/<str:renter_no>/", views.RenterDetailView.as_view(), name="renter-detail"),
    path("owners/", views.PropertyOwnerListCreateView.as_view(), name="owner-list-create"),
    path("owners/<str:owner_no>/", views.PropertyOwnerDetailView.as_view(), name="owner-detail"),
]

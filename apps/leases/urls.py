from django.urls import path

from . import views

urlpatterns = [
    path("", views.LeaseAgreementListCreateView.as_view(), name="lease-list-create"),
    path("<str:lease_no>/", views.LeaseAgreementDetailView.as_view(), name="lease-detail"),
]

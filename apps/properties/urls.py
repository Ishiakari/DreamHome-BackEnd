from django.urls import path

from . import views

urlpatterns = [
    path("", views.PropertyForRentListCreateView.as_view(), name="property-list-create"),
    path("<str:property_no>/", views.PropertyForRentDetailView.as_view(), name="property-detail"),
    path("viewings/", views.PropertyViewingListCreateView.as_view(), name="viewing-list-create"),
    path("viewings/<int:pk>/", views.PropertyViewingDetailView.as_view(), name="viewing-detail"),
    path("inspections/", views.PropertyInspectionListCreateView.as_view(), name="inspection-list-create"),
    path("inspections/<int:pk>/", views.PropertyInspectionDetailView.as_view(), name="inspection-detail"),
    path("adverts/", views.AdvertisementListCreateView.as_view(), name="advert-list-create"),
    path("adverts/<int:pk>/", views.AdvertisementDetailView.as_view(), name="advert-detail"),
]

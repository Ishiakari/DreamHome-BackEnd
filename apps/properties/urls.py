from django.urls import path
from . import views
from .views import MyPropertyViewingListView

urlpatterns = [
    path("my/", views.MyPropertyForRentListView.as_view(), name="my-properties"),
    path("", views.PropertyForRentListCreateView.as_view(), name="property-list-create"),
    path("viewings/my/", MyPropertyViewingListView.as_view(), name="my-viewings"),
    path("viewings/", views.PropertyViewingListCreateView.as_view(), name="viewing-list-create"),
    path("viewings/<int:pk>/", views.PropertyViewingDetailView.as_view(), name="viewing-detail"),
    path("inspections/", views.PropertyInspectionListCreateView.as_view(), name="inspection-list-create"),
    path("inspections/<int:pk>/", views.PropertyInspectionDetailView.as_view(), name="inspection-detail"),
    path("adverts/", views.AdvertisementListCreateView.as_view(), name="advert-list-create"),
    path("adverts/<int:pk>/", views.AdvertisementDetailView.as_view(), name="advert-detail"),
    path("<str:property_no>/", views.PropertyForRentDetailView.as_view(), name="property-detail"),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListCreateView.as_view(), name='payment-list'),
    path('<str:payment_no>/', views.PaymentDetailView.as_view(), name='payment-detail'),
]
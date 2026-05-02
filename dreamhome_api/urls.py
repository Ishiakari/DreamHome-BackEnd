
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.users.serializers import MyTokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/branches/', include('apps.branches.urls')),
    path('api/properties/', include('apps.properties.urls')),
    path('api/leases/', include('apps.leases.urls')),
    path('api/payments/', include('apps.payments.urls')),
    
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

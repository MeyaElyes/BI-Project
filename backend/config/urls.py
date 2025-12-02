"""
URL configuration for Energy Data BI Backend
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    Co2EmissionsViewSet,
    ElectricityProductionViewSet,
    EnergyProdConsViewSet,
    OilProductionViewSet,
)

# Setup DRF router
router = DefaultRouter()
router.register(r'co2-emissions', Co2EmissionsViewSet, basename='co2-emissions')
router.register(r'electricity-production', ElectricityProductionViewSet, basename='electricity-production')
router.register(r'energy-prod-cons', EnergyProdConsViewSet, basename='energy-prod-cons')
router.register(r'oil-production', OilProductionViewSet, basename='oil-production')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]


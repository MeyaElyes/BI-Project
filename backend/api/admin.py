"""
Django admin configuration for Energy Data models
"""

from django.contrib import admin
from .models import (
    CleanedCo2Emissions,
    CleanedElectricityProduction,
    CleanedEnergyProdCons,
    CleanedOilProduction,
)


@admin.register(CleanedCo2Emissions)
class Co2EmissionsAdmin(admin.ModelAdmin):
    list_display = ['entity', 'code', 'year', 'annual_co2_emissions', 'entity_type']
    list_filter = ['entity_type', 'year', 'data_quality_flag']
    search_fields = ['entity', 'code']
    ordering = ['-year', '-annual_co2_emissions']


@admin.register(CleanedElectricityProduction)
class ElectricityProductionAdmin(admin.ModelAdmin):
    list_display = [
        'entity', 
        'code', 
        'year', 
        'electricity_from_coal',
        'electricity_from_gas',
        'electricity_from_nuclear',
        'electricity_from_solar',
        'electricity_from_wind',
        'entity_type'
    ]
    list_filter = ['entity_type', 'year', 'data_quality_flag']
    search_fields = ['entity', 'code']
    ordering = ['-year']


@admin.register(CleanedEnergyProdCons)
class EnergyProdConsAdmin(admin.ModelAdmin):
    list_display = ['entity', 'code', 'year', 'consumption_based_energy', 'production_based_energy', 'entity_type']
    list_filter = ['entity_type', 'year', 'data_quality_flag']
    search_fields = ['entity', 'code']
    ordering = ['-year']


@admin.register(CleanedOilProduction)
class OilProductionAdmin(admin.ModelAdmin):
    list_display = ['entity', 'code', 'year', 'oil_production_twh', 'entity_type']
    list_filter = ['entity_type', 'year', 'data_quality_flag']
    search_fields = ['entity', 'code']
    ordering = ['-year', '-oil_production_twh']


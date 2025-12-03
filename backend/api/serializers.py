"""
Serializers for the Energy Data API
"""

from rest_framework import serializers
from .models import (
    CleanedCo2Emissions,
    CleanedElectricityProduction,
    CleanedEnergyProdCons,
    CleanedOilProduction,
)


class Co2EmissionsSerializer(serializers.ModelSerializer):
    """Serializer for CO2 emissions data"""
    
    class Meta:
        model = CleanedCo2Emissions
        fields = [
            'id',
            'entity',
            'code',
            'year',
            'annual_co2_emissions',
            'data_source',
            'data_quality_flag',
            'last_updated',
            'entity_type',
        ]


class ElectricityProductionSerializer(serializers.ModelSerializer):
    """Serializer for electricity production data"""
    
    class Meta:
        model = CleanedElectricityProduction
        fields = [
            'id',
            'entity',
            'code',
            'year',
            'electricity_from_coal',
            'electricity_from_gas',
            'electricity_from_oil',
            'electricity_from_nuclear',
            'electricity_from_hydro',
            'electricity_from_wind',
            'electricity_from_solar',
            'electricity_from_bioenergy',
            'other_renewables_excluding_bioenergy',
            'data_source',
            'data_quality_flag',
            'last_updated',
            'entity_type',
        ]


class EnergyProdConsSerializer(serializers.ModelSerializer):
    """Serializer for energy production/consumption data"""
    
    class Meta:
        model = CleanedEnergyProdCons
        fields = [
            'id',
            'entity',
            'code',
            'year',
            'consumption_based_energy',
            'production_based_energy',
            'data_source',
            'data_quality_flag',
            'last_updated',
            'entity_type',
        ]


class OilProductionSerializer(serializers.ModelSerializer):
    """Serializer for oil production data"""
    
    class Meta:
        model = CleanedOilProduction
        fields = [
            'id',
            'entity',
            'code',
            'year',
            'oil_production_twh',
            'data_source',
            'data_quality_flag',
            'last_updated',
            'entity_type',
        ]


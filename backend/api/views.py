"""
ViewSets for the Energy Data API
Provides read-only REST endpoints for BI dashboard consumption
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Max, Min

from .models import (
    CleanedCo2Emissions,
    CleanedElectricityProduction,
    CleanedEnergyProdCons,
    CleanedOilProduction,
)
from .serializers import (
    Co2EmissionsSerializer,
    ElectricityProductionSerializer,
    EnergyProdConsSerializer,
    OilProductionSerializer,
)


class Co2EmissionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for CO2 emissions data.
    
    Supports filtering by:
    - entity: country/region name
    - code: country code
    - year: specific year
    - entity_type: 'country' or 'aggregate'
    
    Example: /api/co2-emissions/?entity=France&year=2020
    """
    queryset = CleanedCo2Emissions.objects.all()
    serializer_class = Co2EmissionsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['entity', 'code', 'year']
    ordering_fields = ['year', 'annual_co2_emissions', 'entity']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by query parameters
        entity = self.request.query_params.get('entity', None)
        code = self.request.query_params.get('code', None)
        year = self.request.query_params.get('year', None)
        entity_type = self.request.query_params.get('entity_type', None)
        year_min = self.request.query_params.get('year_min', None)
        year_max = self.request.query_params.get('year_max', None)
        
        if entity:
            queryset = queryset.filter(entity__icontains=entity)
        if code:
            queryset = queryset.filter(code=code)
        if year:
            queryset = queryset.filter(year=year)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        if year_min:
            queryset = queryset.filter(year__gte=year_min)
        if year_max:
            queryset = queryset.filter(year__lte=year_max)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for CO2 emissions"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = queryset.aggregate(
            total_records=Count('id'),
            avg_emissions=Avg('annual_co2_emissions'),
            max_emissions=Max('annual_co2_emissions'),
            min_emissions=Min('annual_co2_emissions'),
            latest_year=Max('year'),
            earliest_year=Min('year'),
        )
        
        return Response(stats)


class ElectricityProductionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for electricity production data.
    
    Supports filtering by:
    - entity: country/region name
    - code: country code
    - year: specific year
    - entity_type: 'country' or 'aggregate'
    
    Example: /api/electricity-production/?entity=Germany&year_min=2015
    """
    queryset = CleanedElectricityProduction.objects.all()
    serializer_class = ElectricityProductionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['entity', 'code', 'year']
    ordering_fields = ['year', 'entity']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        entity = self.request.query_params.get('entity', None)
        code = self.request.query_params.get('code', None)
        year = self.request.query_params.get('year', None)
        entity_type = self.request.query_params.get('entity_type', None)
        year_min = self.request.query_params.get('year_min', None)
        year_max = self.request.query_params.get('year_max', None)
        
        if entity:
            queryset = queryset.filter(entity__icontains=entity)
        if code:
            queryset = queryset.filter(code=code)
        if year:
            queryset = queryset.filter(year=year)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        if year_min:
            queryset = queryset.filter(year__gte=year_min)
        if year_max:
            queryset = queryset.filter(year__lte=year_max)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for electricity production"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = queryset.aggregate(
            total_records=Count('id'),
            avg_fossil=Avg('electricity_from_fossil_fuels_twh'),
            avg_nuclear=Avg('electricity_from_nuclear_twh'),
            avg_renewables=Avg('electricity_from_renewables_twh'),
            total_fossil=Sum('electricity_from_fossil_fuels_twh'),
            total_nuclear=Sum('electricity_from_nuclear_twh'),
            total_renewables=Sum('electricity_from_renewables_twh'),
        )
        
        return Response(stats)


class EnergyProdConsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for energy production/consumption data.
    
    Supports filtering by:
    - entity: country/region name
    - code: country code
    - year: specific year
    - entity_type: 'country' or 'aggregate'
    
    Example: /api/energy-prod-cons/?code=USA
    """
    queryset = CleanedEnergyProdCons.objects.all()
    serializer_class = EnergyProdConsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['entity', 'code', 'year']
    ordering_fields = ['year', 'primary_energy_consumption_twh', 'entity']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        entity = self.request.query_params.get('entity', None)
        code = self.request.query_params.get('code', None)
        year = self.request.query_params.get('year', None)
        entity_type = self.request.query_params.get('entity_type', None)
        year_min = self.request.query_params.get('year_min', None)
        year_max = self.request.query_params.get('year_max', None)
        
        if entity:
            queryset = queryset.filter(entity__icontains=entity)
        if code:
            queryset = queryset.filter(code=code)
        if year:
            queryset = queryset.filter(year=year)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        if year_min:
            queryset = queryset.filter(year__gte=year_min)
        if year_max:
            queryset = queryset.filter(year__lte=year_max)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for energy production/consumption"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = queryset.aggregate(
            total_records=Count('id'),
            avg_consumption=Avg('primary_energy_consumption_twh'),
            max_consumption=Max('primary_energy_consumption_twh'),
            total_consumption=Sum('primary_energy_consumption_twh'),
        )
        
        return Response(stats)


class OilProductionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for oil production data.
    
    Supports filtering by:
    - entity: country/region name
    - code: country code
    - year: specific year
    - entity_type: 'country' or 'aggregate'
    
    Example: /api/oil-production/?entity_type=country&year=2020
    """
    queryset = CleanedOilProduction.objects.all()
    serializer_class = OilProductionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['entity', 'code', 'year']
    ordering_fields = ['year', 'oil_production_twh', 'entity']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        entity = self.request.query_params.get('entity', None)
        code = self.request.query_params.get('code', None)
        year = self.request.query_params.get('year', None)
        entity_type = self.request.query_params.get('entity_type', None)
        year_min = self.request.query_params.get('year_min', None)
        year_max = self.request.query_params.get('year_max', None)
        
        if entity:
            queryset = queryset.filter(entity__icontains=entity)
        if code:
            queryset = queryset.filter(code=code)
        if year:
            queryset = queryset.filter(year=year)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        if year_min:
            queryset = queryset.filter(year__gte=year_min)
        if year_max:
            queryset = queryset.filter(year__lte=year_max)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for oil production"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = queryset.aggregate(
            total_records=Count('id'),
            avg_production=Avg('oil_production_twh'),
            max_production=Max('oil_production_twh'),
            total_production=Sum('oil_production_twh'),
        )
        
        return Response(stats)


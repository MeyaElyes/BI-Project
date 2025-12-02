"""
Tests for the Energy Data API
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status


class Co2EmissionsAPITestCase(APITestCase):
    """Test cases for CO2 emissions endpoint"""
    
    def test_list_co2_emissions(self):
        """Test listing CO2 emissions data"""
        response = self.client.get('/api/co2-emissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_co2_emissions_summary(self):
        """Test CO2 emissions summary endpoint"""
        response = self.client.get('/api/co2-emissions/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_records', response.data)


class ElectricityProductionAPITestCase(APITestCase):
    """Test cases for electricity production endpoint"""
    
    def test_list_electricity_production(self):
        """Test listing electricity production data"""
        response = self.client.get('/api/electricity-production/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_electricity_production_summary(self):
        """Test electricity production summary endpoint"""
        response = self.client.get('/api/electricity-production/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_records', response.data)


class EnergyProdConsAPITestCase(APITestCase):
    """Test cases for energy production/consumption endpoint"""
    
    def test_list_energy_prod_cons(self):
        """Test listing energy prod/cons data"""
        response = self.client.get('/api/energy-prod-cons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)


class OilProductionAPITestCase(APITestCase):
    """Test cases for oil production endpoint"""
    
    def test_list_oil_production(self):
        """Test listing oil production data"""
        response = self.client.get('/api/oil-production/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)


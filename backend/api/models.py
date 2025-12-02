"""
Django models mapped to existing PostgreSQL tables created by Airflow ETL.
These models use managed=False to prevent Django from managing the database schema.
"""

from django.db import models


class CleanedCo2Emissions(models.Model):
    """
    CO2 emissions by country/entity over time.
    Mapped to: cleaned_co2_emissions
    """
    id = models.IntegerField(primary_key=True, db_column='id')
    entity = models.CharField(max_length=255, db_column='entity')
    code = models.CharField(max_length=10, db_column='code', null=True, blank=True)
    year = models.IntegerField(db_column='year')
    annual_co2_emissions = models.FloatField(db_column='annual_co2_emissions', null=True, blank=True)
    data_source = models.CharField(max_length=100, db_column='data_source')
    data_quality_flag = models.CharField(max_length=50, db_column='data_quality_flag')
    last_updated = models.DateField(db_column='last_updated')
    entity_type = models.CharField(max_length=50, db_column='entity_type', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cleaned_co2_emissions'
        ordering = ['-year', '-annual_co2_emissions']
        verbose_name = 'CO2 Emission'
        verbose_name_plural = 'CO2 Emissions'

    def __str__(self):
        return f"{self.entity} - {self.year}"


class CleanedElectricityProduction(models.Model):
    """
    Electricity production by source and country.
    Mapped to: cleaned_electricity_production
    """
    id = models.IntegerField(primary_key=True, db_column='id')
    entity = models.CharField(max_length=255, db_column='entity')
    code = models.CharField(max_length=10, db_column='code', null=True, blank=True)
    year = models.IntegerField(db_column='year')
    other_renewables_excluding_bioenergy = models.FloatField(
        db_column='other_renewables_excluding_bioenergy_twh_adapted_for_visualizat',
        null=True,
        blank=True
    )
    electricity_from_bioenergy = models.FloatField(
        db_column='electricity_from_bioenergy_twh_adapted_for_visualization_of_cha',
        null=True,
        blank=True
    )
    electricity_from_solar = models.FloatField(
        db_column='electricity_from_solar_twh_adapted_for_visualization_of_chart_e',
        null=True,
        blank=True
    )
    electricity_from_wind = models.FloatField(
        db_column='electricity_from_wind_twh_adapted_for_visualization_of_chart_el',
        null=True,
        blank=True
    )
    electricity_from_hydro = models.FloatField(
        db_column='electricity_from_hydro_twh_adapted_for_visualization_of_chart_e',
        null=True,
        blank=True
    )
    electricity_from_nuclear = models.FloatField(
        db_column='electricity_from_nuclear_twh_adapted_for_visualization_of_chart',
        null=True,
        blank=True
    )
    electricity_from_oil = models.FloatField(
        db_column='electricity_from_oil_twh_adapted_for_visualization_of_chart_ele',
        null=True,
        blank=True
    )
    electricity_from_gas = models.FloatField(
        db_column='electricity_from_gas_twh_adapted_for_visualization_of_chart_ele',
        null=True,
        blank=True
    )
    electricity_from_coal = models.FloatField(
        db_column='electricity_from_coal_twh_adapted_for_visualization_of_chart_el',
        null=True,
        blank=True
    )
    data_source = models.CharField(max_length=100, db_column='data_source')
    data_quality_flag = models.CharField(max_length=50, db_column='data_quality_flag')
    last_updated = models.DateField(db_column='last_updated')
    entity_type = models.CharField(max_length=50, db_column='entity_type', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cleaned_electricity_production'
        ordering = ['-year', 'entity']
        verbose_name = 'Electricity Production'
        verbose_name_plural = 'Electricity Production'

    def __str__(self):
        return f"{self.entity} - {self.year}"


class CleanedEnergyProdCons(models.Model):
    """
    Energy production vs consumption by country.
    Mapped to: cleaned_energy_prod_cons
    """
    id = models.IntegerField(primary_key=True, db_column='id')
    entity = models.CharField(max_length=255, db_column='entity')
    code = models.CharField(max_length=10, db_column='code', null=True, blank=True)
    year = models.IntegerField(db_column='year')
    consumption_based_energy = models.FloatField(
        db_column='consumption_based_energy',
        null=True,
        blank=True
    )
    production_based_energy = models.FloatField(
        db_column='production_based_energy',
        null=True,
        blank=True
    )
    data_source = models.CharField(max_length=100, db_column='data_source')
    data_quality_flag = models.CharField(max_length=50, db_column='data_quality_flag')
    last_updated = models.DateField(db_column='last_updated')
    entity_type = models.CharField(max_length=50, db_column='entity_type', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cleaned_energy_prod_cons'
        ordering = ['-year', 'entity']
        verbose_name = 'Energy Production/Consumption'
        verbose_name_plural = 'Energy Production/Consumption'

    def __str__(self):
        return f"{self.entity} - {self.year}"

class CleanedOilProduction(models.Model):
    """
    Oil production by country over time.
    Mapped to: cleaned_oil_production
    """
    id = models.IntegerField(primary_key=True, db_column='id')
    entity = models.CharField(max_length=255, db_column='entity')
    code = models.CharField(max_length=10, db_column='code', null=True, blank=True)
    year = models.IntegerField(db_column='year')
    oil_production_twh = models.FloatField(
        db_column='oil_production_twh',
        null=True,
        blank=True
    )
    data_source = models.CharField(max_length=100, db_column='data_source')
    data_quality_flag = models.CharField(max_length=50, db_column='data_quality_flag')
    last_updated = models.DateField(db_column='last_updated')
    entity_type = models.CharField(max_length=50, db_column='entity_type', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cleaned_oil_production'
        ordering = ['-year', '-oil_production_twh']
        verbose_name = 'Oil Production'
        verbose_name_plural = 'Oil Production'

    def __str__(self):
        return f"{self.entity} - {self.year}"


"""
File: backend/model.py
Description:
    This file defines database 'models' using SQLModel.

    Each class represents a table in the PostgreSQL database.
    - `table=True` indicates to SQLModel that this is a database table.
    - `Field(...)` is used to provide additional information such as
      primary_key, index, and foreign_key constraints.
    
    Defined tables:
    - Province: Dimension table containing information for 63 provinces/cities.
    - ClimateData: Fact table containing annual climate data by province.
    - SoilData: Fact table containing soil data by province.
    - AgricultureData: Primary fact table containing agricultural data
      (production, area, yield) by year, region/province, commodity, and season.
"""

from sqlmodel import SQLModel, Field
from typing import Optional

# --- 1. Province Table (Dimension Table) ---
class Province(SQLModel, table=True):
    """
    Model for the 'province' table.
    Stores static information (coordinates, etc.) for each province.
    """
    __tablename__ = "province"
    id: Optional[int] = Field(default=None, primary_key=True)
    province_name: str = Field(unique=True, index=True) 
    
    latitude_center: Optional[float] = None
    longitude_center: Optional[float] = None
    latitude_min: Optional[float] = None
    latitude_max: Optional[float] = None
    longitude_min: Optional[float] = None
    longitude_max: Optional[float] = None

# --- 2. Climate Data Table (Fact Table) ---
class ClimateData(SQLModel, table=True):
    """
    Model for the 'climate_data' table.
    Stores annual climate data.
    """
    __tablename__ = "climate_data"
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int = Field(index=True)
    #province_name: str = Field(index=True) 
    
    avg_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    surface_temperature: Optional[float] = None
    wet_bulb_temperature: Optional[float] = None
    precipitation: Optional[float] = None
    solar_radiation: Optional[float] = None
    relative_humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    surface_pressure: Optional[float] = None

    # Foreign key - connection to Province table
    province_id: int = Field(foreign_key="province.id")

# --- 3. Soil Data Table (Fact Table) ---
class SoilData(SQLModel, table=True):
    """
    Model for the 'soil_data' table.
    Stores fixed soil data for each province.
    """
    __tablename__ = "soil_data"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    surface_elevation: Optional[float] = None
    avg_ndvi: Optional[float] = None
    soil_ph_level: Optional[float] = None
    soil_organic_carbon: Optional[float] = None
    soil_nitrogen_content: Optional[float] = None
    soil_sand_ratio: Optional[float] = None
    soil_clay_ratio: Optional[float] = None

    # Foreign key - connection to Province table
    province_id: Optional[int] = Field(
        default=None, 
        foreign_key="province.id"
    )

# --- 4. Agriculture Data Table (Fact Table) ---
class AgricultureData(SQLModel, table=True):
    """
    Model for the 'agriculture_data' table.
    Stores agricultural data (production, area, yield).
    This is the primary fact table.
    """
    __tablename__ = "agriculture_data"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    year: int = Field(index=True)
    commodity: str = Field(index=True)
    season: Optional[str] = Field(index=True)
    
    area_thousand_ha: Optional[float] = None
    yield_ta_per_ha: Optional[float] = None
    production_thousand_tonnes: Optional[float] = None

    region_name: str = Field(index=True)
    region_level: str = Field(index=True)

    # Foreign key - connection to Province table
    province_id: Optional[int] = Field(
        default=None, 
        foreign_key="province.id"
    )
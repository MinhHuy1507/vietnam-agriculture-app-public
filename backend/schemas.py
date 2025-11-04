"""
File: backend/schemas.py
Description:
    This file defines Pydantic/SQLModel 'schemas' used for
    data validation and serialization for API endpoints.

    These classes serve as "API Contracts":
    - They define exactly which fields are returned
      to users (Frontend).
    - They help FastAPI automatically filter out internal fields (such as 'province_id')
      from API responses.

    Defined classes:
    - ProvinceRead: Response schema for Province table.
    - ClimateDataRead: Response schema for Climate table (with JOIN, includes 'province_name').
    - SoilDataRead: Response schema for Soil table (with JOIN, includes 'province_name').
    - AgricultureDataRead: Response schema for Agriculture table.
"""
from sqlmodel import SQLModel
from typing import Optional

# --- 1. SCHEMAS FOR PROVINCE ---
class ProvinceBase(SQLModel):
    province_name: str
    latitude_center: Optional[float] = None
    longitude_center: Optional[float] = None
    latitude_min: Optional[float] = None
    latitude_max: Optional[float] = None
    longitude_min: Optional[float] = None
    longitude_max: Optional[float] = None

class ProvinceRead(ProvinceBase):
    """
    Response schema (Read) for Province data.
    Specifies fields that will be sent when API calls /provinces.
    """
    id: int

# --- 2. SCHEMAS FOR AGRICULTURE DATA ---
class AgricultureDataRead(SQLModel):
    """
    Response schema (Read) for Agriculture data.
    Intentionally EXCLUDES 'province_id' (foreign key) to
    avoid exposing database details through the API.
    """
    id: int
    year: int
    commodity: str
    season: Optional[str] = None
    area_thousand_ha: Optional[float] = None
    yield_ta_per_ha: Optional[float] = None
    production_thousand_tonnes: Optional[float] = None
    region_name: str
    region_level: str

# --- 3. SCHEMAS FOR CLIMATE DATA ---
class ClimateDataRead(SQLModel):
    """
    Response schema (Read) for Climate data.
    This schema includes 'province_name' (from JOIN)
    and intentionally EXCLUDES 'province_id'.
    """
    id: int
    year: int
    province_name: str
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

# --- 4. SCHEMAS FOR SOIL DATA ---
class SoilDataRead(SQLModel):
    """
    Response schema (Read) for Soil data.
    This schema includes 'province_name' (from JOIN)
    and intentionally EXCLUDES 'province_id'.
    """
    id: int
    province_name: str
    surface_elevation: Optional[float] = None
    avg_ndvi: Optional[float] = None
    soil_ph_level: Optional[float] = None
    soil_organic_carbon: Optional[float] = None
    soil_nitrogen_content: Optional[float] = None
    soil_sand_ratio: Optional[float] = None
    soil_clay_ratio: Optional[float] = None

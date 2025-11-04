"""
File: backend/dependencies.py
Description:
    This file defines Pydantic 'BaseModel' classes used for
    Dependency Injection in FastAPI.

    Instead of defining 10 parameters (e.g., year, commodity, ...)
    in an API function, These query classes group them into these classes.
    FastAPI automatically recognizes these classes and converts them
    into Query Parameters for the API.

    Defined classes:
    - Enums (Year, Commodity, Season, RegionLevel): Define fixed choice values,
      providing dropdown functionality in Swagger UI and automatic input validation.
    - AgricultureQuery: Groups filter parameters for the agriculture-data API.
    - ClimateQuery: Groups filter parameters for the climate-data API.
    - SoilQuery: Groups filter parameters for the soil-data API.
    - PredictionInput: Defines the 21 input features for the prediction API.
    - PredictionOutput: Defines the JSON response structure of the prediction API.
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum

# --- 1. ENUMS (FIXED CHOICE VALUES) (Support for Swagger UI display) ---
class Year(int, Enum):
    Y1995 = 1995
    Y1996 = 1996
    Y1997 = 1997
    Y1998 = 1998
    Y1999 = 1999
    Y2000 = 2000
    Y2001 = 2001
    Y2002 = 2002
    Y2003 = 2003
    Y2004 = 2004
    Y2005 = 2005
    Y2006 = 2006
    Y2007 = 2007
    Y2008 = 2008
    Y2009 = 2009
    Y2010 = 2010
    Y2011 = 2011
    Y2012 = 2012
    Y2013 = 2013
    Y2014 = 2014
    Y2015 = 2015
    Y2016 = 2016
    Y2017 = 2017
    Y2018 = 2018
    Y2019 = 2019
    Y2020 = 2020
    Y2021 = 2021
    Y2022 = 2022
    Y2023 = 2023
    Y2024 = 2024

class Commodity(str, Enum):
    rice = "rice"
    maize = "maize"
    cassava = "cassava"
    sweet_potato = "sweet_potato"
    sugarcane = "sugarcane"

class Season(str, Enum):
    annual = "annual"
    winter_spring = "winter_spring"
    summer_autumn_fall = "summer_autumn_fall"
    main_rainy = "main_rainy"

class RegionLevel(str, Enum):
    province = "province"
    region = "region"
    country = "country"

# --- 2. QUERY PARAMETER CLASSES ---
class AgricultureQuery(BaseModel):
    """
    Groups filter parameters (query params) for the /agriculture-data API.
    FastAPI will automatically handle Depends() for this class.
    """
    year: Optional[Year] = None
    commodity: Optional[Commodity] = None
    season: Optional[Season] = None
    region_level: Optional[RegionLevel] = None
    region_name: Optional[str] = None

class ClimateQuery(BaseModel):
    """
    Groups filter parameters (query params) for the /climate-data API.
    """
    year: Optional[Year] = None
    province_name: Optional[str] = None

class SoilQuery(BaseModel):
    """
    Groups filter parameters (query params) for the /soil-data API.
    """
    province_name: Optional[str] = None

class PredictionInput(BaseModel):
    """
    Defines the structure (schema) of the 21 input features
    that the /predict API will receive (as JSON body).
    """
    province_name: str
    year: int
    commodity: str
    season: str
    
    # 10 climate factors
    avg_temperature: Optional[float] = 0.0
    min_temperature: Optional[float] = 0.0
    max_temperature: Optional[float] = 0.0
    surface_temperature: Optional[float] = 0.0
    wet_bulb_temperature: Optional[float] = 0.0
    precipitation: Optional[float] = 0.0
    solar_radiation: Optional[float] = 0.0
    relative_humidity: Optional[float] = 0.0
    wind_speed: Optional[float] = 0.0
    surface_pressure: Optional[float] = 0.0
    
    # 7 soil factors
    surface_elevation: Optional[float] = 0.0
    avg_ndvi: Optional[float] = 0.0
    soil_ph_level: Optional[float] = 0.0
    soil_organic_carbon: Optional[float] = 0.0
    soil_nitrogen_content: Optional[float] = 0.0
    soil_sand_ratio: Optional[float] = 0.0
    soil_clay_ratio: Optional[float] = 0.0

class PredictionOutput(BaseModel):
    """
    Defines the JSON response structure
    of the /predict API.
    """
    predicted_production: float
    predicted_area: float
    predicted_yield: float
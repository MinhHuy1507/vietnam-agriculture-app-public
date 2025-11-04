"""
File: backend/dependencies.py
Description:
    File này định nghĩa các Pydantic 'BaseModel' được sử dụng cho
    Dependency Injection (Tiêm phụ thuộc) trong FastAPI.

    Thay vì định nghĩa 10 tham số (ví dụ: year, commodity, ...)
    trên một hàm API, chúng ta nhóm chúng vào các class này.
    FastAPI sẽ tự động "hiểu" các class này và biến chúng thành
    các tham số truy vấn (Query Parameters) trên API.

    Các class được định nghĩa:
    - Enums (Year, Commodity, Season, RegionLevel): Định nghĩa các giá trị
      lựa chọn cố định, giúp tạo dropdown trên Swagger UI và tự động
      xác thực (validate) dữ liệu đầu vào.
    - AgricultureQuery: Nhóm các tham số lọc cho API agriculture-data.
    - ClimateQuery: Nhóm các tham số lọc cho API climate-data.
    - SoilQuery: Nhóm các tham số lọc cho API soil-data.
    - PredictionInput: Định nghĩa 21 features đầu vào cho API dự đoán.
    - PredictionOutput: Định nghĩa cấu trúc JSON trả về của API dự đoán.
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum

# --- 1. ENUMS (ĐỊNH NGHĨA CÁC LỰA CHỌN CỐ ĐỊNH) (Hỗ trợ hiển thị trên Swagger UI) ---
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

# --- 2. CÁC CLASS TRUY VẤN (QUERY PARAMS) ---
class AgricultureQuery(BaseModel):
    """
    Nhóm các tham số lọc (query params) cho API /agriculture-data.
    FastAPI sẽ tự động "Depends()" class này.
    """
    year: Optional[Year] = None
    commodity: Optional[Commodity] = None
    season: Optional[Season] = None
    region_level: Optional[RegionLevel] = None
    region_name: Optional[str] = None

class ClimateQuery(BaseModel):
    """
    Nhóm các tham số lọc (query params) cho API /climate-data.
    """
    year: Optional[Year] = None
    province_name: Optional[str] = None

class SoilQuery(BaseModel):
    """
    Nhóm các tham số lọc (query params) cho API /soil-data.
    """
    province_name: Optional[str] = None

class PredictionInput(BaseModel):
    """
    Định nghĩa cấu trúc (schema) của 21 features đầu vào
    mà API /predict sẽ nhận (dưới dạng JSON body).
    """
    province_name: str
    year: int
    commodity: str
    season: str
    
    # 10 yếu tố khí hậu
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
    
    # 7 yếu tố thổ nhưỡng
    surface_elevation: Optional[float] = 0.0
    avg_ndvi: Optional[float] = 0.0
    soil_ph_level: Optional[float] = 0.0
    soil_organic_carbon: Optional[float] = 0.0
    soil_nitrogen_content: Optional[float] = 0.0
    soil_sand_ratio: Optional[float] = 0.0
    soil_clay_ratio: Optional[float] = 0.0

class PredictionOutput(BaseModel):
    """
    Định nghĩa cấu trúc (schema) JSON trả về
    của API /predict.
    """
    predicted_production: float
    predicted_area: float
    predicted_yield: float
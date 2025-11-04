"""
File: backend/schemas.py
Description:
    File này định nghĩa các 'schemas' (lược đồ) Pydantic/SQLModel
    được sử dụng để xác thực (validate) và tuần tự hóa (serialize)
    dữ liệu cho các API endpoint.

    Các class này đóng vai trò là "Hợp đồng API":
    - Chúng định nghĩa chính xác các trường (field) nào được trả về
      cho người dùng (Frontend).
    - Chúng giúp FastAPI tự động lọc bỏ các trường nội bộ (như 'province_id')
      ra khỏi response (phản hồi) API.

    Các class được định nghĩa:
    - ProvinceRead: Schema trả về cho Bảng Tỉnh.
    - ClimateDataRead: Schema trả về cho Bảng Khí hậu (đã JOIN, có 'province_name').
    - SoilDataRead: Schema trả về cho Bảng Thổ nhưỡng (đã JOIN, có 'province_name').
    - AgricultureDataRead: Schema trả về cho Bảng Nông nghiệp.
"""
from sqlmodel import SQLModel
from typing import Optional

# --- 1. SCHEMAS CHO PROVINCE ---
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
    Schema trả về (Read) cho dữ liệu Tỉnh.
    Chỉ định các trường sẽ được gửi khi API gọi /provinces.
    """
    id: int

# --- 2. SCHEMAS CHO AGRICULTURE DATA ---
class AgricultureDataRead(SQLModel):
    """
    Schema trả về (Read) cho dữ liệu Nông nghiệp.
    Cố tình BỎ QUA 'province_id' (khóa ngoại) để
    không làm lộ chi tiết CSDL ra bên ngoài API.
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

# --- 3. SCHEMAS CHO CLIMATE DATA ---
class ClimateDataRead(SQLModel):
    """
    Schema trả về (Read) cho dữ liệu Khí hậu.
    Schema này bao gồm 'province_name' (được JOIN vào)
    và cố tình BỎ QUA 'province_id'.
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

# --- 4. SCHEMAS CHO SOIL DATA ---
class SoilDataRead(SQLModel):
    """
    Schema trả về (Read) cho dữ liệu Thổ nhưỡng.
    Schema này bao gồm 'province_name' (được JOIN vào)
    và cố tình BỎ QUA 'province_id'.
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

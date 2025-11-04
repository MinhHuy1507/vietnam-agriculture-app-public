"""
File: backend/model.py
Description:
    File này định nghĩa 'models' (mô hình) cho Cơ sở dữ liệu (CSDL)
    sử dụng SQLModel.

    Mỗi class ở đây đại diện cho một bảng (table) trong CSDL PostgreSQL.
    - `table=True` báo cho SQLModel biết đây là một bảng CSDL.
    - `Field(...)` được dùng để cung cấp các thông tin bổ sung như
      khóa chính (primary_key), chỉ mục (index), và khóa ngoại (foreign_key).
    
    Các bảng được định nghĩa:
    - Province: Bảng tra cứu (dimension) chứa thông tin 63 tỉnh thành.
    - ClimateData: Bảng sự kiện (fact) chứa dữ liệu khí hậu hàng năm theo tỉnh.
    - SoilData: Bảng sự kiện (fact) chứa dữ liệu thổ nhưỡng (đất) theo tỉnh.
    - AgricultureData: Bảng sự kiện (fact) chính chứa dữ liệu nông nghiệp
      (sản lượng, diện tích, năng suất) theo năm, vùng/tỉnh, nông sản, mùa vụ.
"""

from sqlmodel import SQLModel, Field
from typing import Optional

# --- 1. Bảng Province (Dimension Table) ---
class Province(SQLModel, table=True):
    """
    Mô hình cho bảng 'province'.
    Lưu trữ thông tin tĩnh (tọa độ, v.v.) cho mỗi tỉnh.
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

# --- 2. Bảng Khí hậu (Fact Table) ---
class ClimateData(SQLModel, table=True):
    """
    Mô hình cho bảng 'climate_data'.
    Lưu trữ dữ liệu khí hậu hàng năm.
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

    # Foreign key - connect to Province
    province_id: int = Field(foreign_key="province.id")

# --- 3. Bảng Thổ nhưỡng (Fact Table) ---
class SoilData(SQLModel, table=True):
    """
    Mô hình cho bảng 'soil_data'.
    Lưu trữ dữ liệu thổ nhưỡng (đất) cố định cho mỗi tỉnh.
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

    # Foreign key - connect to Province
    province_id: Optional[int] = Field(
        default=None, 
        foreign_key="province.id"
    )

# --- 4. Bảng Nông nghiệp (Fact Table) ---
class AgricultureData(SQLModel, table=True):
    """
    Mô hình cho bảng 'agriculture_data'.
    Lưu trữ dữ liệu nông nghiệp (sản lượng, diện tích, năng suất).
    Đây là bảng "sự kiện" chính.
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

    # Foreign key - connect to Province
    province_id: Optional[int] = Field(
        default=None, 
        foreign_key="province.id"
    )
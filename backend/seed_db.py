"""
File: backend/seed_db.py
Description:
    Đây là một script (kịch bản) chạy độc lập dùng để "nạp mồi" (seed)
    dữ liệu từ các file CSV (trong thư mục /data) vào CSDL PostgreSQL.
    
    Script này KHÔNG PHẢI là một phần của API, mà là một công cụ
    tiện ích chạy 1 lần để thiết lập môi trường CSDL.
    
    Nó cũng được 'docker-compose.yml' (dịch vụ 'db-seeder') sử dụng
    để tự động nạp dữ liệu khi khởi chạy.

    Quy trình chạy:
    1. reset_database(): Xóa (DROP) và tạo lại (CREATE) tất cả các bảng.
    2. insert_provinces_data(): Nạp dữ liệu tỉnh (bảng 'province').
    3. get_province_id(): Tạo một 'bản đồ' (dictionary) tra cứu
       từ {province_name -> id} để dùng cho các khóa ngoại.
    4. insert_soil_data(): Nạp dữ liệu đất, dùng 'bản đồ' ở trên để
       điền 'province_id'.
    5. insert_climate_data(): Nạp dữ liệu khí hậu, dùng 'bản đồ' ở trên
       để điền 'province_id'.
    6. insert_agriculture_data(): Nạp dữ liệu nông nghiệp, dùng 'bản đồ'
       ở trên để điền 'province_id' (cho các hàng 'province').
"""
import pandas as pd
from sqlmodel import Session, SQLModel
from utils.connect_database import engine
from model import Province, ClimateData, AgricultureData
import os

# Định nghĩa đường dẫn tuyệt đối đến thư mục 'data'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def reset_database():
    """
    Xóa (DROP) tất cả các bảng CSDL và tạo lại (CREATE) chúng
    dựa trên 'model.py'. Đảm bảo một khởi đầu "sạch".
    """
    try:
        print("Resetting database")

        SQLModel.metadata.drop_all(engine) 
        SQLModel.metadata.create_all(engine)
        
        print("Reset database successfully")
    except Exception as e:
        print(f"Error resetting database: {e}")
        raise e
    
def insert_provinces_data(path: str):
    """
    Nạp dữ liệu từ 'province.csv' vào bảng 'province'.
    Đây là bảng "cha", phải được nạp đầu tiên.
    """
    try:
        print("Inserting provinces data")
        df_province = pd.read_csv(path)
        df_province.to_sql(
            name="province",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted provinces data successfully")
    except Exception as e:
        print(f"Error inserting provinces: {e}")

def get_province_id():
    """
    Đọc lại bảng 'province' (sau khi đã nạp) để tạo một 
    dictionary tra cứu (map) {province_name -> id}.
    Ví dụ: {'An Giang': 1, 'Ba Ria - Vung Tau': 2, ...}
    
    Returns:
        dict: Một dictionary tra cứu tên tỉnh và ID.
    """
    with Session(engine) as session:
        df_province_from_db = pd.read_sql("SELECT id, province_name FROM province", session.connection())
        province_map = pd.Series(df_province_from_db.id.values, 
                                 index=df_province_from_db.province_name).to_dict()
    return province_map


def insert_climate_data(path: str):
    """
    Nạp dữ liệu 'climate.csv' vào bảng 'climate_data'.
    Sử dụng 'province_map' để điền khóa ngoại 'province_id'.
    """
    try:
        print("Inserting climate data")
        df_climate = pd.read_csv(path)
        province_map = get_province_id()
        
        df_climate['province_id'] = df_climate['province_name'].map(province_map)
        df_climate = df_climate.drop(columns=['province_name'])
        
        df_climate.to_sql(
            name="climate_data",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted climate data successfully")
    except Exception as e:
        print(f"Error inserting climate data: {e}")

def insert_soil_data(path: str):
    """
    Nạp dữ liệu 'soil.csv' vào bảng 'soil_data'.
    Sử dụng 'province_map' để điền khóa ngoại 'province_id'.
    """
    try:
        print("Inserting soil data")
        df_soil = pd.read_csv(path)
        province_map = get_province_id()

        df_soil['province_id'] = df_soil['province_name'].map(province_map)
        df_soil = df_soil.drop(columns=['province_name'])

        df_soil.to_sql(
            name="soil_data",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted soil data successfully")
    except Exception as e:
        print(f"Error inserting soil data: {e}")

def insert_agriculture_data(path: str):
    """
    Nạp dữ liệu 'agriculture.csv' vào bảng 'agriculture_data'.
    Sử dụng 'province_map' để điền khóa ngoại 'province_id'
    cho các hàng có 'region_level' là 'province'.
    """
    try:
        print("Inserting agriculture data")
        df_agriculture = pd.read_csv(path)
        province_map = get_province_id()
        
        df_agriculture['province_id'] = df_agriculture['region_name'].map(province_map)
        level_map = {
            1: "province",
            2: "region",
            3: "country"
        }
        df_agriculture['region_level'] = df_agriculture['region_level'].map(level_map)

        df_agriculture.to_sql(
            name="agriculture_data",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted agriculture data successfully")
    except Exception as e:
        print(f"Error inserting agriculture data: {e}")

# MAIN
if __name__ == "__main__":
    """
    Đây là hàm main, chỉ chạy khi script này
    được gọi trực tiếp (ví dụ: 'python seed_db.py').
    """
    reset_database()
    insert_provinces_data(os.path.join(DATA_DIR, "province.csv"))
    insert_climate_data(os.path.join(DATA_DIR, "climate.csv"))
    insert_agriculture_data(os.path.join(DATA_DIR, "agriculture.csv"))
    insert_soil_data(os.path.join(DATA_DIR, "soil.csv"))
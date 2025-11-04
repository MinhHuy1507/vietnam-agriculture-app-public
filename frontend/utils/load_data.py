"""
File: frontend/utils/load_data.py
Description:
    Đây là file tiện ích (utility) TRUNG TÂM, chịu trách nhiệm
    tải tất cả dữ liệu cho ứng dụng Streamlit.
    
    Các trang con (trong thư mục /pages) sẽ 'import' các hàm từ file này
    thay vì tự định nghĩa logic gọi API.
"""

import streamlit as st
import pandas as pd
import requests
import os

# --- 1. ĐỊNH NGHĨA API BASE URL ---
# Đọc URL API từ biến môi trường, nếu không có thì dùng localhost
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

# --- 2. HÀM GỌI API (HÀM "CON") ---
@st.cache_data(ttl=600)
def load_all_data_from_api(endpoint: str, params: dict = {}):
    """
    Hàm gọi API chung, tự động xử lý phân trang để lấy TẤT CẢ dữ liệu.
    """
    all_data = []
    page_size = 1000  
    skip = 0
    current_params = params.copy()
    current_params.pop('limit', None)
    current_params.pop('skip', None)
    current_params['limit'] = page_size
    current_params['skip'] = skip

    while True:
        try:
            full_url = f"{API_BASE_URL}/{endpoint}"
            response = requests.get(full_url, params=current_params)
            
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break 
                all_data.extend(data)
                skip += page_size
                current_params['skip'] = skip
            else:
                st.error(f"Lỗi khi gọi API {endpoint}: {response.status_code}")
                return pd.DataFrame() 
        except Exception as e:
            st.error(f"Lỗi kết nối API: {e}")
            return pd.DataFrame()
    
    return pd.DataFrame(all_data)

# --- 3. HÀM TẢI DỮ LIỆU CHỦ (HÀM "MẸ") ---
@st.cache_data(ttl=600)
def load_master_data():
    """
    Tải tất cả các nguồn dữ liệu chính từ API một lần duy nhất.
    Hàm này sẽ được các trang con gọi.
    """
    with st.spinner("Đang tải dữ liệu chính (master data)..."):
        df_agri = load_all_data_from_api("statistics/agriculture-data")
        df_provinces = load_all_data_from_api("statistics/provinces")
        df_climate = load_all_data_from_api("statistics/climate-data")
        df_soil = load_all_data_from_api("statistics/soil-data")
        
        # Lấy df_regions từ df_agri
        df_regions = df_agri[df_agri['region_level'] == 'region']

        # Xử lý kiểu dữ liệu (rất quan trọng cho việc lọc)
        if 'year' in df_agri.columns:
            df_agri['year'] = pd.to_numeric(df_agri['year'], errors='coerce')
        if 'year' in df_climate.columns:
            df_climate['year'] = pd.to_numeric(df_climate['year'], errors='coerce')
                
        return df_agri, df_provinces, df_regions, df_climate, df_soil
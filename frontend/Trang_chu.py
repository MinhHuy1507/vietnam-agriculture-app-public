"""
File: frontend/Trang_chu.py
Description:
    Đây là file chạy chính (entrypoint) cho ứng dụng Streamlit Frontend.
    File này chịu trách nhiệm:
    1. Cấu hình trang (st.set_page_config) ở chế độ wide (rộng).
    2. Tải toàn bộ dữ liệu (master data) từ API và lưu vào st.session_state MỘT LẦN DUY NHẤT
       khi ứng dụng khởi động.
    3. Định nghĩa và chạy menu điều hướng đa trang (st.navigation) hiển thị ở sidebar.
    4. Hiển thị nội dung cho Trang chủ (trang chào mừng).
"""

import os
import streamlit as st
import requests
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Dashboard Nông nghiệp VN",
    page_icon="🌾",
    layout="wide"
)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

# --- 2. HÀM GỌI API ---
@st.cache_data(ttl=600)
def load_all_data_from_api(endpoint: str, params: dict = {}):
    """
    Hàm gọi API chung, tự động xử lý phân trang để lấy TẤT CẢ dữ liệu.

    Hàm này sẽ gọi API lặp đi lặp lại (mỗi lần 1000 hàng) cho đến khi
    API trả về một danh sách rỗng, sau đó ghép tất cả lại.

    Args:
        endpoint (str): Đường dẫn API (ví dụ: "statistics/agriculture-data").
        params (dict, optional): Các tham số truy vấn (query params) ban đầu.

    Returns:
        pd.DataFrame: Một DataFrame chứa toàn bộ dữ liệu.
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
                st.error(f"Lỗi khi gọi API {endpoint} (trang {skip // page_size}): {response.status_code}")
                return pd.DataFrame() 
        except Exception as e:
            st.error(f"Lỗi kết nối API: {e}")
            return pd.DataFrame()
    
    return pd.DataFrame(all_data)

# --- 3. TẢI DỮ LIỆU CHỦ (MASTER DATA) VÀO SESSION ---
@st.cache_data(ttl=600)
def load_master_data():
    """
    Tải tất cả các nguồn dữ liệu chính từ API một lần duy nhất.
    Dữ liệu này sẽ được lưu vào st.session_state để các trang con sử dụng.
    """
    df_agri = load_all_data_from_api("statistics/agriculture-data")
    df_provinces = load_all_data_from_api("statistics/provinces")
    df_regions = load_all_data_from_api("statistics/agriculture-data", params={"region_level": "region"})
    df_climate = load_all_data_from_api("statistics/climate-data")
    df_soil = load_all_data_from_api("statistics/soil-data")

    if 'year' in df_agri.columns:
        df_agri['year'] = pd.to_numeric(df_agri['year'], errors='coerce')
    if 'year' in df_climate.columns:
        df_climate['year'] = pd.to_numeric(df_climate['year'], errors='coerce')
            
    return df_agri, df_provinces, df_regions, df_climate, df_soil

if 'data_loaded' not in st.session_state:
    st.session_state.df_agri_master, \
    st.session_state.df_provinces_master, \
    st.session_state.df_regions_master, \
    st.session_state.df_climate_master, \
    st.session_state.df_soil_master = load_master_data()
    st.session_state.data_loaded = True

# --- 4. ĐỊNH NGHĨA NỘI DUNG TRANG CHỦ ---
def show_home_page():
    st.title("🌾 Chào mừng đến với Dashboard Nông nghiệp Việt Nam")
    st.markdown("---")
    st.header("Giới thiệu dự án")
    st.write("""
        Đây là một dự án data engineer end-to-end, trình bày khả năng xây dựng
        một hệ thống hoàn chỉnh từ thu thập dữ liệu (Pipeline), lưu trữ (Data Lake),
        xây dựng API (Backend) cho đến trực quan hóa (Frontend).
    """)
    st.info("Vui lòng chọn một trang phân tích từ thanh điều hướng bên trái để bắt đầu.", icon="👈")

# --- 5. TẠO ĐIỀU HƯỚNG TÙY CHỈNH ---
pages = [
    st.Page(show_home_page, title="Trang chủ", icon="🏠", default=True), 
    
    # Các trang con
    st.Page("pages/1_Phân_tích_Nông_nghiệp.py", title="Phân tích Nông nghiệp", icon="📊"),
    st.Page("pages/2_Phân_tích_Địa_lý.py", title="Phân tích Địa lý", icon="🗺️"),
    st.Page("pages/3_Phân_tích_Khí_hậu.py", title="Phân tích Khí hậu", icon="☀️"),
    st.Page("pages/4_Phân_tích_Thổ_nhưỡng.py", title="Phân tích Thổ nhưỡng", icon="🌱"),
    st.Page("pages/5_Dự_đoán_số_liệu.py", title="Dự đoán Số liệu", icon="🔮"),
]
nav = st.navigation(pages)

# --- 6. CHẠY TRANG ĐƯỢC CHỌN ---
nav.run()
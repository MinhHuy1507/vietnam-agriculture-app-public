"""
File: frontend/Trang_chu.py
Description:
    This is the main entry point for the Streamlit Frontend application.
    This file is responsible for:
    1. Configuring the page (st.set_page_config) in wide layout mode.
    2. Defining and running the multi-page navigation menu (st.navigation) displayed in the sidebar.
    3. Displaying content for the Home page (welcome page).
"""
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dashboard Nông nghiệp VN",
    page_icon="🌾",
    layout="wide"
)

# --- 2. DEFINE HOME PAGE CONTENT ---
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

# --- 3. CREATE CUSTOM NAVIGATION ---
pages = [
    st.Page(show_home_page, title="Trang chủ", icon="🏠", default=True), 
    
    # Other pages
    st.Page("pages/1_Phan_tich_Nong_nghiep.py", title="Phân tích Nông nghiệp", icon="📊"),
    st.Page("pages/2_Phan_tich_Dia_ly.py", title="Phân tích Địa lý", icon="🗺️"),
    st.Page("pages/3_Phan_tich_Khi_hau.py", title="Phân tích Khí hậu", icon="☀️"),
    st.Page("pages/4_Phan_tich_Tho_nhuong.py", title="Phân tích Thổ nhưỡng", icon="🌱"),
    st.Page("pages/5_Du_doan_So_lieu.py", title="Dự đoán Số liệu", icon="🔮"),
]
nav = st.navigation(pages)

# --- 4. RUN SELECTED PAGE ---
nav.run()
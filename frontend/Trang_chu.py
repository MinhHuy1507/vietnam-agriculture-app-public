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
        Dự án này đóng vai trò là **Lớp Ứng dụng (Application Layer)** trong một hệ sinh thái Kỹ thuật Dữ liệu (Data Engineering) toàn diện. 
        Nó minh họa khả năng xây dựng một hệ thống hoàn chỉnh từ khâu thu thập dữ liệu, lưu trữ, xử lý cho đến trực quan hóa.
        
        Hệ thống bao gồm Backend (FastAPI) và Frontend (Streamlit) hoạt động độc lập, phục vụ việc phân tích và trực quan hóa dữ liệu nông nghiệp Việt Nam.
    """)

    st.subheader("🔗 Các dự án liên quan")
    st.markdown("""
    Ứng dụng này là lớp hiển thị (visualization layer). Để hiểu rõ quy trình dữ liệu được thu thập và xử lý, vui lòng tham khảo các dự án nguồn:

    *   **[Vietnam Agriculture Data Lake](https://github.com/MinhHuy1507/vietnam-agriculture-datalake-public)**
        *   **Vai trò:** Thu thập & Lưu trữ dữ liệu.
        *   **Chức năng:** Thu thập dữ liệu thô từ Tổng cục Thống kê (GSO), NASA POWER, Google Earth Engine.

    *   **[Vietnam Agriculture Data Warehouse](https://github.com/MinhHuy1507/vietnam-agriculture-data-warehouse-public)**
        *   **Vai trò:** Chuyển đổi & Mô hình hóa dữ liệu.
        *   **Chức năng:** Xây dựng Kho dữ liệu (Star Schema) từ Data Lake sử dụng Airflow và dbt.
    """)

    st.info("Vui lòng chọn một trang phân tích từ thanh điều hướng bên trái để bắt đầu.", icon="👈")

# --- 3. CREATE CUSTOM NAVIGATION ---
pages = [
    st.Page(show_home_page, title="Trang chủ", icon="🏠", default=True), 
    
    # Other pages
    st.Page("pages/1_Phân_tích_Nông_nghiệp.py", title="Phân tích Nông nghiệp", icon="📊"),
    st.Page("pages/2_Phân_tích_Địa_lý.py", title="Phân tích Địa lý", icon="🗺️"),
    st.Page("pages/3_Phân_tích_Khí_hậu.py", title="Phân tích Khí hậu", icon="☀️"),
    st.Page("pages/4_Phân_tích_Thổ_nhưỡng.py", title="Phân tích Thổ nhưỡng", icon="🌱"),
    st.Page("pages/5_Dự_đoán_số_liệu.py", title="Dự đoán Số liệu", icon="🔮"),
]
nav = st.navigation(pages)

# --- 4. RUN SELECTED PAGE ---
nav.run()
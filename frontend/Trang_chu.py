"""
File: frontend/Trang_chu.py
Description:
    Đây là file chạy chính (entrypoint) cho ứng dụng Streamlit Frontend.
    File này chịu trách nhiệm:
    1. Cấu hình trang (st.set_page_config) ở chế độ wide (rộng)..
    2. Định nghĩa và chạy menu điều hướng đa trang (st.navigation) hiển thị ở sidebar.
    3. Hiển thị nội dung cho Trang chủ (trang chào mừng).
"""
import streamlit as st

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Dashboard Nông nghiệp VN",
    page_icon="🌾",
    layout="wide"
)

# --- 2. ĐỊNH NGHĨA NỘI DUNG TRANG CHỦ ---
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

# --- 3. TẠO ĐIỀU HƯỚNG TÙY CHỈNH ---
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

# --- 4. CHẠY TRANG ĐƯỢC CHỌN ---
nav.run()
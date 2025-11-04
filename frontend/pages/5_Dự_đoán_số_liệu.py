"""
File: pages/5_Dự_đoán.py
Description:
    This is the "Prediction" page of the application.
    This page is responsible for:
    1. Retrieving master data that has been pre-loaded from st.session_state
       (especially df_soil_master and df_climate_master to get fixed values
       and historical averages).
    2. Displaying a form (st.form) for user input.
    3. Clear separation:
        - Basic factors (Province, Commodity) - OUTSIDE form for
          automatic updating of fixed information.
        - Soil information (Fixed, read-only) - OUTSIDE form.
        - Climate factors (Forecast, user input) - INSIDE form.
    4. When "Predict" is clicked, the logic will:
        - Collect all 21 features (inputs).
        - "Impute" climate values left blank by user (set to 0)
          with historical average values for that province.
        - Send a POST request to the /predict API.
        - Display results (Production, Area, Yield) returned from API.
"""
import os
import streamlit as st
import pandas as pd
import requests
from utils.load_data import load_master_data

# --- 1. RETRIEVE DATA ---
df_agri_master, df_provinces_master, df_regions_master, df_climate_master, df_soil_master = load_master_data()
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

# --- 2. PAGE 5 CONTENT: PREDICTION ---
st.title("🔮 Trang Dự đoán Sản lượng")
st.markdown("Nhập các thông số dự kiến để nhận dự đoán về Sản lượng, Diện tích và Năng suất.")
st.info("Trang này hiện đang chạy với logic 'giả' (mock). Mô hình ML thật có thể được tích hợp vào API sau.")

# --- 3. BASIC FILTERS ---
st.header("Yếu tố Cơ bản (Bắt buộc)")
col1, col2 = st.columns(2)
with col1:
    province_list = sorted(df_provinces_master['province_name'].unique())
    selected_province = st.selectbox(
        "Chọn Tỉnh:", options=province_list, index=0, key="pred_province"
    )
    
    commodity_list = sorted(df_agri_master['commodity'].unique())
    selected_commodity = st.selectbox(
        "Chọn Nông sản:", options=commodity_list, index=0, key="pred_commodity"
    )
with col2:
    selected_year = st.number_input(
        "Năm dự đoán:", min_value=2025, max_value=2050, 
        value=2025, step=1, key="pred_year"
    )
    
    season_list = sorted(df_agri_master['season'].dropna().unique())
    selected_season = st.selectbox(
        "Chọn Mùa vụ:", options=season_list, index=0, key="pred_season"
    )

# --- 4. DISPLAY SOIL INFORMATION ---
st.markdown("---")
st.subheader("Thông tin Thổ nhưỡng (Cố định)")
st.info(f"Các đặc tính đất dưới đây là cố định cho tỉnh **{selected_province}** và sẽ được tự động sử dụng trong dự đoán.", icon="ℹ️")

# Retrieve soil data for selected province
soil_data = df_soil_master[df_soil_master['province_name'] == selected_province]

if not soil_data.empty:
    soil_data_row = soil_data.iloc[0]
    
    scol1, scol2, scol3 = st.columns(3)
    with scol1:
        st.metric(label="Độ cao (m)", value=f"{soil_data_row.get('surface_elevation', 0.0):,.0f}")
        st.metric(label="Độ pH", value=f"{soil_data_row.get('soil_ph_level', 0.0):,.2f}")
        st.metric(label="Chỉ số NDVI", value=f"{soil_data_row.get('avg_ndvi', 0.0):,.3f}")
    with scol2:
        st.metric(label="Hàm lượng Carbon Hữu cơ (%)", value=f"{soil_data_row.get('soil_organic_carbon', 0.0):,.2f} %")
        st.metric(label="Hàm lượng Nitơ (%)", value=f"{soil_data_row.get('soil_nitrogen_content', 0.0):,.4f} %")
    with scol3:
        st.metric(label="Hàm lượng Cát (%)", value=f"{soil_data_row.get('soil_sand_ratio', 0.0):,.1f} %")
        st.metric(label="Hàm lượng Sét (%)", value=f"{soil_data_row.get('soil_clay_ratio', 0.0):,.1f} %")
else:
    st.warning(f"Không tìm thấy dữ liệu thổ nhưỡng cho tỉnh {selected_province}.")

# --- 5. INPUT FORM ---
with st.form(key="prediction_form"):
    
    st.markdown("---")
    st.header("Yếu tố Khí hậu (Dự báo)")
    st.markdown("Nhập các giá trị dự báo. Nếu để `0`, hệ thống sẽ dùng giá trị trung bình lịch sử của tỉnh đó.")
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        pred_avg_temp = st.number_input("Nhiệt độ TB (°C)", key="pred_avg_temp", value=0.0, format="%.2f")
        pred_min_temp = st.number_input("Nhiệt độ Min (°C)", key="pred_min_temp", value=0.0, format="%.2f")
        pred_max_temp = st.number_input("Nhiệt độ Max (°C)", key="pred_max_temp", value=0.0, format="%.2f")
        pred_wet_bulb = st.number_input("Nhiệt độ Bầu ướt (°C)", key="pred_wet_bulb", value=0.0, format="%.2f")
    with c_col2:
        pred_precip = st.number_input("Lượng mưa (mm)", key="pred_precip", value=0.0, format="%.2f")
        pred_solar = st.number_input("Bức xạ (kW-hr/m^2/day)", key="pred_solar", value=0.0, format="%.2f")
        pred_humid = st.number_input("Độ ẩm (%)", key="pred_humid", value=0.0, format="%.2f")
    with c_col3:
        pred_wind = st.number_input("Sức gió (m/s)", key="pred_wind", value=0.0, format="%.2f")
        pred_pressure = st.number_input("Áp suất (kPa)", key="pred_pressure", value=0.0, format="%.2f")
        pred_surf_temp = st.number_input("Nhiệt độ Bề mặt (°C)", key="pred_surf_temp", value=0.0, format="%.2f")

    # Submit button
    submitted = st.form_submit_button("Dự đoán")

# --- 6. PROCESSING LOGIC WHEN BUTTON IS CLICKED ---
if submitted:
    with st.spinner("Đang xử lý dự đoán..."):
        
        if soil_data.empty:
            st.error(f"Không thể dự đoán vì thiếu dữ liệu thổ nhưỡng cho {selected_province}.")
            st.stop()
        
        # Retrieve historical averages for the province
        hist_climate = df_climate_master[df_climate_master['province_name'] == selected_province].mean(numeric_only=True)
        
        def get_value(pred_val, hist_val_key):
            # Check if hist_val_key doesn't exist
            if hist_val_key not in hist_climate or pd.isna(hist_climate[hist_val_key]):
                return pred_val if pred_val != 0.0 else 0.0
            return pred_val if pred_val != 0.0 else hist_climate[hist_val_key]

        # Package 21 features (Payload)
        input_data = {
            "province_name": selected_province,
            "year": selected_year,
            "commodity": selected_commodity,
            "season": selected_season,

            # Get from form widget
            "avg_temperature": get_value(pred_avg_temp, 'avg_temperature'),
            "min_temperature": get_value(pred_min_temp, 'min_temperature'),
            "max_temperature": get_value(pred_max_temp, 'max_temperature'),
            "surface_temperature": get_value(pred_surf_temp, 'surface_temperature'),
            "wet_bulb_temperature": get_value(pred_wet_bulb, 'wet_bulb_temperature'),
            "precipitation": get_value(pred_precip, 'precipitation'),
            "solar_radiation": get_value(pred_solar, 'solar_radiation'),
            "relative_humidity": get_value(pred_humid, 'relative_humidity'),
            "wind_speed": get_value(pred_wind, 'wind_speed'),
            "surface_pressure": get_value(pred_pressure, 'surface_pressure'),
            
            # Get from soil_data_row
            "surface_elevation": soil_data_row.get('surface_elevation', 0.0),
            "avg_ndvi": soil_data_row.get('avg_ndvi', 0.0),
            "soil_ph_level": soil_data_row.get('soil_ph_level', 0.0),
            "soil_organic_carbon": soil_data_row.get('soil_organic_carbon', 0.0),
            "soil_nitrogen_content": soil_data_row.get('soil_nitrogen_content', 0.0),
            "soil_sand_ratio": soil_data_row.get('soil_sand_ratio', 0.0),
            "soil_clay_ratio": soil_data_row.get('soil_clay_ratio', 0.0)
        }
        
        # Call API
        try:
            response = requests.post(f"{API_BASE_URL}/predict", json=input_data)
            
            if response.status_code == 200:
                results = response.json()
                st.success("Dự đoán thành công!")
                st.header("Kết quả Dự đoán")
                
                res_col1, res_col2, res_col3 = st.columns(3)
                res_col1.metric(
                    "Sản lượng Dự đoán", 
                    f"{results['predicted_production']:,.0f} Nghìn Tấn"
                )
                res_col2.metric(
                    "Diện tích Dự đoán", 
                    f"{results['predicted_area']:,.0f} Nghìn Ha"
                )
                res_col3.metric(
                    "Năng suất Dự đoán", 
                    f"{results['predicted_yield']:,.2f} Tạ/Ha"
                )
                
                with st.expander("Xem chi tiết Dữ liệu đầu vào (đã xử lý)"):
                    st.json(input_data)

            else:
                st.error(f"Lỗi từ API: {response.status_code} - {response.text}")
                
        except Exception as e:
            st.error(f"Lỗi kết nối đến API: {e}")
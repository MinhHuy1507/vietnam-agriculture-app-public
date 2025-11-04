"""
File: pages/3_Phân_tích_Khí_hậu.py
Description:
    This is the "Climate Analysis" page of the application.
    This page is responsible for:
    1. Retrieving data.
    2. Displaying 2 tabs: "Climate Trends" and "Correlation (with Agriculture)".
    3. "Trends" tab: Allows users to select 1 Province and 1 year range,
       then displays charts (Line, Bar) for all climate metrics.
    4. "Correlation" tab: Allows users to select Province, Commodity, Agricultural Metric
       and Climate Metric to analyze relationships (dual-axis and scatter plot).
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.load_data import load_master_data

# --- 1. RETRIEVE DATA ---
df_agri_master, df_provinces_master, df_regions_master, df_climate_master, df_soil_master = load_master_data()

# --- 2. PAGE 4 CONTENT: CLIMATE ---
st.title("☀️ Phân tích Khí hậu")

tab1, tab2 = st.tabs([
    "Phân tích Xu hướng Khí hậu", 
    "Phân tích Tương quan (với Nông nghiệp)"
])

# --- TAB 1 CONTENT: CLIMATE ANALYSIS ---
with tab1:
    st.header("Xu hướng Khí hậu qua các năm")
    st.markdown("Chọn một tỉnh và một khoảng năm để xem các chỉ số khí hậu thay đổi như thế nào.")
    
    # --- TAB 1 FILTERS ---
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            province_list_tab1 = sorted(df_climate_master['province_name'].unique())
            selected_province_tab1 = st.selectbox(
                "Chọn Tỉnh:", options=province_list_tab1,
                index=0, key="p4_tab1_province"
            )
        with col2:
            min_year = int(df_climate_master['year'].min())
            max_year = int(df_climate_master['year'].max())
            selected_year_range_tab1 = st.slider(
                "Chọn khoảng năm:", min_value=min_year, max_value=max_year,
                value=(min_year, max_year), step=1, key="p4_tab1_years"
            )
    
    # FILTER DATA FOR TAB 1
    df_climate_tab1 = df_climate_master[
        (df_climate_master['province_name'] == selected_province_tab1) &
        (df_climate_master['year'] >= selected_year_range_tab1[0]) &
        (df_climate_master['year'] <= selected_year_range_tab1[1])
    ].sort_values(by='year')

    if not df_climate_tab1.empty:
        st.markdown("---")
        
        # Chart 1: Temperature
        st.subheader(f"Xu hướng Nhiệt độ tại {selected_province_tab1}")
        temp_cols = [
            'avg_temperature', 'min_temperature', 'max_temperature', 
            'surface_temperature', 'wet_bulb_temperature'
        ]
        temp_labels = {
            'avg_temperature': 'Nhiệt độ TB',
            'min_temperature': 'Nhiệt độ Min',
            'max_temperature': 'Nhiệt độ Max',
            'surface_temperature': 'Nhiệt độ Bề mặt',
            'wet_bulb_temperature': 'Nhiệt độ Bầu ướt'
        }
        fig_temp = px.line(
            df_climate_tab1, x='year', y=temp_cols,
            title="Các loại Nhiệt độ (°C)",
            labels={'year': 'Năm', 'value': 'Nhiệt độ (°C)', 'variable': 'Loại nhiệt độ'},
            markers=True
        )
        fig_temp.for_each_trace(lambda t: t.update(name = temp_labels.get(t.name, t.name)))
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Charts 2 & 3: Precipitation & Radiation
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Xu hướng Lượng mưa")
            fig_precip = px.bar(
                df_climate_tab1, x='year', y='precipitation',
                title="Tổng Lượng mưa hàng năm (mm)",
                labels={'year': 'Năm', 'precipitation': 'Lượng mưa (mm)'}
            )
            st.plotly_chart(fig_precip, use_container_width=True)
        with col_chart2:
            st.subheader("Xu hướng Bức xạ")
            fig_solar = px.line(
                df_climate_tab1, x='year', y='solar_radiation',
                title="Bức xạ mặt trời (kW-hr/m^2/day)",
                labels={'year': 'Năm', 'solar_radiation': 'Bức xạ'},
                markers=True, color_discrete_sequence=['orange']
            )
            st.plotly_chart(fig_solar, use_container_width=True)

        # Charts 4, 5, 6: Humidity, Wind, Pressure
        col_chart3, col_chart4, col_chart5 = st.columns(3)
        with col_chart3:
            st.subheader("Xu hướng Độ ẩm")
            fig_humid = px.line(
                df_climate_tab1, x='year', y='relative_humidity',
                title="Độ ẩm tương đối (%)",
                labels={'year': 'Năm', 'relative_humidity': 'Độ ẩm (%)'},
                markers=True, color_discrete_sequence=['green']
            )
            st.plotly_chart(fig_humid, use_container_width=True)
        with col_chart4:
            st.subheader("Xu hướng Sức gió")
            fig_wind = px.line(
                df_climate_tab1, x='year', y='wind_speed',
                title="Sức gió (tại 2m) (m/s)",
                labels={'year': 'Năm', 'wind_speed': 'Sức gió (m/s)'},
                markers=True, color_discrete_sequence=['gray']
            )
            st.plotly_chart(fig_wind, use_container_width=True)
        with col_chart5:
            st.subheader("Xu hướng Áp suất")
            fig_pressure = px.line(
                df_climate_tab1, x='year', y='surface_pressure',
                title="Áp suất bề mặt (kPa)",
                labels={'year': 'Năm', 'surface_pressure': 'Áp suất (kPa)'},
                markers=True, color_discrete_sequence=['purple']
            )
            st.plotly_chart(fig_pressure, use_container_width=True)
    else:
        st.warning("Không tìm thấy dữ liệu khí hậu cho lựa chọn này.")


# --- TAB 2 CONTENT: CORRELATION ANALYSIS ---
with tab2:
    st.header("Phân tích Tương quan Nông nghiệp & Khí hậu")
    st.markdown("So sánh sự thay đổi của các chỉ số nông nghiệp với các yếu tố khí hậu tại một tỉnh.")

    # --- TAB 2 FILTERS ---
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        # Select Province and Commodity
        with col1:
            province_list_tab2 = sorted(df_climate_master['province_name'].unique())
            selected_province_tab2 = st.selectbox(
                "Chọn Tỉnh:", options=province_list_tab2,
                index=0, key="p4_tab2_province"
            )
            
            commodity_list_tab2 = ["Tất cả"] + sorted(df_agri_master['commodity'].unique())
            selected_commodity_tab2 = st.selectbox(
                "Chọn Nông sản (để tính tổng):",
                options=commodity_list_tab2, index=0, key="p4_tab2_commodity"
            )
        
        # Select Year Range and Agricultural Metric
        with col2:
            min_year_tab2 = int(df_climate_master['year'].min())
            max_year_tab2 = int(df_climate_master['year'].max())
            selected_year_range_tab2 = st.slider(
                "Chọn khoảng năm:", min_value=min_year_tab2, max_value=max_year_tab2,
                value=(min_year_tab2, max_year_tab2), step=1, key="p4_tab2_years"
            )
            
            agri_metric_options = {
                "Năng suất": "yield_ta_per_ha",
                "Sản lượng": "production_thousand_tonnes",
                "Diện tích": "area_thousand_ha"
            }
            selected_agri_label = st.selectbox(
                "Chọn chỉ số Nông nghiệp:",
                options=list(agri_metric_options.keys()),
                key="p4_tab2_agri_metric"
            )
            selected_agri_col = agri_metric_options[selected_agri_label]

        # Select Climate Metric
        with col3:
            climate_metric_options = {
                "Nhiệt độ Trung bình": "avg_temperature",
                "Nhiệt độ thấp nhất": "min_temperature",
                "Nhiệt độ cao nhất": "max_temperature",
                "Nhiệt độ bề mặt": "surface_temperature",
                "Nhiệt độ bầu ướt": "wet_bulb_temperature",
                "Lượng mưa": "precipitation",
                "Bức xạ Mặt trời": "solar_radiation",
                "Độ ẩm": "relative_humidity",
                "Sức gió": "wind_speed",
                "Áp suất Bề mặt": "surface_pressure"
            }
            selected_climate_label = st.selectbox(
                "Chọn chỉ số Khí hậu:",
                options=list(climate_metric_options.keys()),
                key="p4_tab2_climate_metric"
            )
            selected_climate_col = climate_metric_options[selected_climate_label]

    # --- FILTER DATA FOR TAB 2 ---
    
    # 1. Filter Climate data
    df_climate_tab2 = df_climate_master[
        (df_climate_master['province_name'] == selected_province_tab2) &
        (df_climate_master['year'] >= selected_year_range_tab2[0]) &
        (df_climate_master['year'] <= selected_year_range_tab2[1])
    ].sort_values(by='year')

    # 2. Filter Agriculture data
    df_agri_tab2 = df_agri_master[
        (df_agri_master['region_name'] == selected_province_tab2) &
        (df_agri_master['region_level'] == 'province') &
        (df_agri_master['year'] >= selected_year_range_tab2[0]) &
        (df_agri_master['year'] <= selected_year_range_tab2[1])
    ]
    if selected_commodity_tab2 != "Tất cả":
        df_agri_tab2 = df_agri_tab2[df_agri_tab2['commodity'] == selected_commodity_tab2]
    
    # (Handle nulls)
    df_agri_tab2['production_thousand_tonnes'] = pd.to_numeric(df_agri_tab2['production_thousand_tonnes'], errors='coerce')
    df_agri_tab2['area_thousand_ha'] = pd.to_numeric(df_agri_tab2['area_thousand_ha'], errors='coerce')
    df_agri_tab2['yield_ta_per_ha'] = pd.to_numeric(df_agri_tab2['yield_ta_per_ha'], errors='coerce')
    mask_yield = df_agri_tab2['yield_ta_per_ha'].isnull() & df_agri_tab2['production_thousand_tonnes'].notnull() & df_agri_tab2['area_thousand_ha'].notnull() & (df_agri_tab2['area_thousand_ha'] > 0)
    df_agri_tab2.loc[mask_yield, 'yield_ta_per_ha'] = (df_agri_tab2['production_thousand_tonnes'] / df_agri_tab2['area_thousand_ha']) * 10

    # Group agriculture data by year
    df_agri_trend_tab2 = df_agri_tab2.groupby('year')[selected_agri_col].sum().reset_index()

    # 3. Merge both datasets
    df_corr = pd.merge(df_climate_tab2, df_agri_trend_tab2, on='year', how='inner')
    
    # CREATE DYNAMIC TITLE
    if selected_commodity_tab2 == "Tất cả":
        dynamic_agri_label = f"{selected_agri_label} (Tổng)"
    else:
        dynamic_agri_label = f"{selected_agri_label} ({selected_commodity_tab2})"

    if not df_corr.empty:
        st.markdown("---")
        
        # Chart 1: Correlation over time (Dual-axis)
        st.subheader(f"Xu hướng {dynamic_agri_label} vs. {selected_climate_label}")
        
        fig_corr_time = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Agricultural metric
        fig_corr_time.add_trace(
            go.Bar(x=df_corr['year'], y=df_corr[selected_agri_col], name=dynamic_agri_label),
            secondary_y=False,
        )
        # Climate metric
        fig_corr_time.add_trace(
            go.Scatter(x=df_corr['year'], y=df_corr[selected_climate_col], name=selected_climate_label, mode='lines+markers'),
            secondary_y=True,
        )
        
        fig_corr_time.update_layout(title_text=f"Tương quan theo thời gian tại {selected_province_tab2}")
        fig_corr_time.update_xaxes(title_text="Năm")
        fig_corr_time.update_yaxes(title_text=f"<b>{dynamic_agri_label}</b>", secondary_y=False)
        fig_corr_time.update_yaxes(title_text=f"<b>{selected_climate_label}</b>", secondary_y=True)
        st.plotly_chart(fig_corr_time, use_container_width=True)

        # Chart 2: Direct correlation (Scatter Plot)
        st.subheader(f"Phân tích Tương quan trực tiếp")
        
        fig_scatter = px.scatter(
            df_corr,
            x=selected_climate_col,
            y=selected_agri_col,
            title=f"Tương quan giữa {selected_climate_label} (trục X) và {dynamic_agri_label} (trục Y)",
            labels={selected_climate_col: selected_climate_label, selected_agri_col: dynamic_agri_label},
            trendline="ols"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    else:
        st.warning("Không tìm thấy dữ liệu nông nghiệp và khí hậu trùng khớp cho lựa chọn này.")
"""
File: pages/4_Phân_tích_Thổ_nhưỡng.py
Description:
    This is the "Soil Analysis" page of the application.
    This page is responsible for:
    1. Retrieving data.
    2. Assuming soil data has been normalized (e.g., %) from the database.
    3. Displaying 2 tabs: "Soil Distribution" and "Correlation (Soil & Agriculture)".
    4. "Distribution" tab: Visualizes 1 soil metric (e.g., pH, Nitrogen)
    for all provinces on a bar chart.
    5. "Correlation" tab: Analyzes relationships (scatter plot) between
    1 soil metric (X-axis) and 1 agricultural metric (averaged over years, Y-axis).
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.load_data import load_master_data

# --- 1. RETRIEVE DATA ---
df_agri_master, df_provinces_master, df_regions_master, df_climate_master, df_soil_master = load_master_data()

# --- 2. PAGE 4 CONTENT: SOIL ---
st.title("🌱 Phân tích Thổ nhưỡng (Đất)")

tab1, tab2 = st.tabs([
    "Phân bố Thổ nhưỡng (Toàn quốc)", 
    "Tương quan (Đất & Nông nghiệp)"
])

# --- CREATE SELECTION DICTIONARY ---
SOIL_METRIC_OPTIONS = {
    "Độ cao (m)": "surface_elevation",
    "Chỉ số NDVI (Độ xanh)": "avg_ndvi",
    "Độ pH": "soil_ph_level",
    "Hàm lượng Carbon Hữu cơ (%)": "soil_organic_carbon",
    "Hàm lượng Nitơ (%)": "soil_nitrogen_content",
    "Hàm lượng Cát (%)": "soil_sand_ratio",
    "Hàm lượng Sét (%)": "soil_clay_ratio"
}

# --- TAB 1: DISTRIBUTION (MAP & BAR CHART) ---
with tab1:
    st.header("Phân bố các Chỉ số Đất")
    st.markdown("Xem xét sự khác biệt về chất lượng đất giữa các tỉnh.")
    
    # TAB 1 FILTERS
    with st.container(border=True):
        selected_soil_label_t1 = st.selectbox(
            "Chọn chỉ số đất để phân tích:",
            options=list(SOIL_METRIC_OPTIONS.keys()),
            key="p5_tab1_metric"
        )
        selected_soil_col_t1 = SOIL_METRIC_OPTIONS[selected_soil_label_t1]

    if not df_soil_master.empty:
        df_plot = df_soil_master.dropna(subset=[selected_soil_col_t1])

        st.markdown("---")
        
        # Bar chart
        st.subheader(f"Xếp hạng các tỉnh theo {selected_soil_label_t1}")
        df_bar = df_plot.sort_values(by=selected_soil_col_t1, ascending=False)
        fig_bar = px.bar(
            df_bar,
            x='province_name',
            y=selected_soil_col_t1,
            title=f"So sánh {selected_soil_label_t1} giữa các tỉnh",
            labels={'province_name': 'Tỉnh', selected_soil_col_t1: selected_soil_label_t1},
            color=selected_soil_col_t1,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    else:
        st.warning("Không tìm thấy dữ liệu thổ nhưỡng.")


# --- TAB 2: CORRELATION (SOIL & AGRICULTURE) ---
with tab2:
    st.header("Phân tích Tương quan: Đất & Năng suất")
    st.markdown("Khám phá xem các yếu tố thổ nhưỡng (trục X) ảnh hưởng đến năng suất nông nghiệp (trục Y) như thế nào.")

    # --- TAB 2 FILTERS ---
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        # Filter agricultural metric (Y-axis)
        with col1:
            agri_metric_options = {
                "Năng suất (TB)": "yield_ta_per_ha",
                "Sản lượng (TB)": "production_thousand_tonnes",
                "Diện tích (TB)": "area_thousand_ha"
            }
            selected_agri_label_t2 = st.selectbox(
                "Chỉ số Nông nghiệp (Trục Y):",
                options=list(agri_metric_options.keys()),
                key="p5_tab2_agri_metric"
            )
            selected_agri_col_t2 = agri_metric_options[selected_agri_label_t2]
        
        # Filter soil metric (X-axis)
        with col2:
            soil_metric_options_t2 = SOIL_METRIC_OPTIONS.copy()
            selected_soil_label_t2 = st.selectbox(
                "Chỉ số Thổ nhưỡng (Trục X):",
                options=list(soil_metric_options_t2.keys()),
                key="p5_tab2_soil_metric"
            )
            selected_soil_col_t2 = soil_metric_options_t2[selected_soil_label_t2]

        # Filter commodity
        with col3:
            commodity_list_tab2 = ["Tất cả"] + sorted(df_agri_master['commodity'].unique())
            selected_commodity_tab2 = st.selectbox(
                "Lọc theo Nông sản:",
                options=commodity_list_tab2, index=0,
                key="p5_tab2_commodity"
            )
            
    # --- FILTER AND PREPARE CORRELATION DATA ---
    
    # 1. Filter Agriculture data (only province level)
    df_agri_corr = df_agri_master[df_agri_master['region_level'] == 'province']
    
    if selected_commodity_tab2 != "Tất cả":
        df_agri_corr = df_agri_corr[df_agri_corr['commodity'] == selected_commodity_tab2]
    
    # (Handle nulls)
    df_agri_corr['production_thousand_tonnes'] = pd.to_numeric(df_agri_corr['production_thousand_tonnes'], errors='coerce')
    df_agri_corr['area_thousand_ha'] = pd.to_numeric(df_agri_corr['area_thousand_ha'], errors='coerce')
    df_agri_corr['yield_ta_per_ha'] = pd.to_numeric(df_agri_corr['yield_ta_per_ha'], errors='coerce')
    mask_yield = df_agri_corr['yield_ta_per_ha'].isnull() & df_agri_corr['production_thousand_tonnes'].notnull() & df_agri_corr['area_thousand_ha'].notnull() & (df_agri_corr['area_thousand_ha'] > 0)
    df_agri_corr.loc[mask_yield, 'yield_ta_per_ha'] = (df_agri_corr['production_thousand_tonnes'] / df_agri_corr['area_thousand_ha']) * 10
    
    # CALCULATE AVERAGE AGRICULTURE DATA OVER YEARS
    df_agri_avg = df_agri_corr.groupby('region_name')[selected_agri_col_t2].mean().reset_index()

    # 2. Merge with Soil Data
    df_corr = pd.merge(
        df_soil_master,
        df_agri_avg,
        left_on='province_name',
        right_on='region_name',
        how='inner'
    )

    # --- DISPLAY TAB 2 CONTENT ---
    if not df_corr.empty:
        st.markdown("---")
        
        # Correlation Chart (Scatter Plot)
        st.subheader(f"Tương quan: {selected_soil_label_t2} vs. {selected_agri_label_t2}")
        
        fig_scatter = px.scatter(
            df_corr,
            x=selected_soil_col_t2,
            y=selected_agri_col_t2,
            title=f"Tương quan (Nông sản: {selected_commodity_tab2})",
            labels={
                selected_soil_col_t2: f"{selected_soil_label_t2} (Đất)",
                selected_agri_col_t2: f"{selected_agri_label_t2} (Nông nghiệp)"
            },
            trendline="ols",
            hover_name="province_name"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    else:
        st.warning("Không tìm thấy dữ liệu trùng khớp cho lựa chọn này.")
"""
File: frontend/pages/1_Phân_tích_Nông_nghiệp.py
Description:
    This is the "Agriculture Analysis" page of the application.
    This page is responsible for:
    1. Retrieving data.
    2. Displaying 2 tabs: "Overview" and "In-depth Analysis".
    3. "Overview" tab: Provides filters for a SINGLE YEAR and
    displays KPI metrics, distribution charts (Bar, Pie, Treemap).
    4. "In-depth Analysis" tab: Provides "Slicer" filters (multi-select) to
    compare trends across multiple years.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.load_data import load_master_data

# --- 1. RETRIEVE DATA ---
df_agri_master, df_provinces_master, df_regions_master, df_climate_master, df_soil_master = load_master_data()

# --- 2. CREATE 2 TABS: OVERVIEW AND IN-DEPTH ---
st.title("📊 Phân tích Số liệu Nông nghiệp")
tab1, tab2 = st.tabs([
    "Tổng quan (Snapshot)", 
    "Phân tích Chuyên sâu (Trends & Comparisons)"
])

# --- TAB 1 CONTENT ---
with tab1:
    st.header("Tổng quan (Snapshot)")
    st.markdown("Xem xét dữ liệu tại một thời điểm cụ thể (năm).")

    # TAB 1 FILTERS
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            region_levels = ["country", "region", "province"]
            selected_level = st.selectbox("Cấp độ:", region_levels, index=0, key="p1_level")
        
        with col2:
            if selected_level == "region":
                region_list = ["Tất cả"] + sorted(df_regions_master['region_name'].unique().tolist())
                selected_region = st.selectbox("Chọn Vùng:", region_list, key="p1_region", disabled=False)
            elif selected_level == "province":
                province_list = ["Tất cả"] + sorted(df_provinces_master['province_name'].unique().tolist())
                selected_region = st.selectbox("Chọn Tỉnh:", province_list, key="p1_region", disabled=False)
            else:
                selected_region = st.selectbox("Khu vực:", ["- (Cả nước) -"], index=0, key="p1_region", disabled=True)
                selected_region = "Tất cả"
        
        with col3:
            min_year = int(df_agri_master['year'].min())
            max_year = int(df_agri_master['year'].max())
            selected_year = st.slider(
                "Chọn Năm:", min_value=min_year, max_value=max_year,
                value=max_year, step=1, key="p1_year"
            )
        with col4:
            commodity_list = ["Tất cả"] + sorted(df_agri_master['commodity'].unique())
            selected_commodity = st.selectbox("Nông sản:", commodity_list, index=0, key="p1_commodity")
        with col5:
            season_list = ["Tất cả"] + sorted(df_agri_master['season'].dropna().unique())
            selected_season = st.selectbox("Mùa vụ:", season_list, index=0, key="p1_season")

    # FILTER DATA FOR TAB 1
    df_page1 = df_agri_master.copy()
    df_page1 = df_page1[df_page1['year'] == selected_year]
    if selected_level != "Tất cả":
        df_page1 = df_page1[df_page1['region_level'] == selected_level]
    if selected_region != "Tất cả":
        df_page1 = df_page1[df_page1['region_name'] == selected_region]
    if selected_commodity != "Tất cả":
        df_page1 = df_page1[df_page1['commodity'] == selected_commodity]
    if selected_season != "Tất cả":
        df_page1 = df_page1[df_page1['season'] == selected_season]

    # DISPLAY TAB 1 CONTENT
    if not df_page1.empty:
        st.markdown("---")
        st.subheader(f"Chỉ số KPI cho năm {selected_year}")     
        
        # --- Handle Null Values ---
        """
        Some records are missing one of three metrics: production, area, yield.
        Apply formula to calculate missing metric when possible.
        yield (quintals/ha) = production (1000 tonnes) / area (1000 ha) * 10
        """
        df_page1['production_thousand_tonnes'] = pd.to_numeric(df_page1['production_thousand_tonnes'], errors='coerce')
        df_page1['area_thousand_ha'] = pd.to_numeric(df_page1['area_thousand_ha'], errors='coerce')
        df_page1['yield_ta_per_ha'] = pd.to_numeric(df_page1['yield_ta_per_ha'], errors='coerce')
        mask_yield = df_page1['yield_ta_per_ha'].isnull() & df_page1['production_thousand_tonnes'].notnull() & df_page1['area_thousand_ha'].notnull() & (df_page1['area_thousand_ha'] > 0)
        df_page1.loc[mask_yield, 'yield_ta_per_ha'] = (df_page1['production_thousand_tonnes'] / df_page1['area_thousand_ha']) * 10
        mask_prod = df_page1['production_thousand_tonnes'].isnull() & df_page1['yield_ta_per_ha'].notnull() & df_page1['area_thousand_ha'].notnull()
        df_page1.loc[mask_prod, 'production_thousand_tonnes'] = (df_page1['yield_ta_per_ha'] * df_page1['area_thousand_ha']) / 10
        mask_area = df_page1['area_thousand_ha'].isnull() & df_page1['yield_ta_per_ha'].notnull() & df_page1['production_thousand_tonnes'].notnull() & (df_page1['yield_ta_per_ha'] > 0)
        df_page1.loc[mask_area, 'area_thousand_ha'] = (df_page1['production_thousand_tonnes'] / df_page1['yield_ta_per_ha']) * 10
        
        # --- Calculate KPIs (after handling nulls) ---
        total_production = df_page1['production_thousand_tonnes'].sum()
        total_area = df_page1['area_thousand_ha'].sum()
        avg_yield = (total_production / total_area) * 10 if total_area > 0 else 0

        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric(label="Tổng Sản lượng (Nghìn Tấn)", value=f"{total_production:,.0f}")
        col_kpi2.metric(label="Tổng Diện tích (Nghìn Ha)", value=f"{total_area:,.0f}")
        col_kpi3.metric(label="Năng suất Trung bình (Tạ/Ha)", value=f"{avg_yield:,.2f}")
        
        # --- DISTRIBUTION CHARTS (Dynamic) ---
        st.markdown("---") 
        st.subheader(f"Phân tích Nông sản chi tiết năm {selected_year}")
        
        col_filter1, col_filter2 = st.columns(2)
        # Filter to select Metric
        with col_filter1:
            metric_options = {"Sản lượng": "production_thousand_tonnes", "Diện tích": "area_thousand_ha", "Năng suất": "yield_ta_per_ha"}
            selected_metric_label = st.selectbox("Chọn chỉ số để phân tích:", options=list(metric_options.keys()), key="p1_metric_selector")
            selected_metric_col = metric_options[selected_metric_label]
            units = {"production_thousand_tonnes": "Nghìn Tấn", "area_thousand_ha": "Nghìn Ha", "yield_ta_per_ha": "Tạ/Ha"}
            selected_unit = units[selected_metric_col]
        # Filter to select Chart Type
        with col_filter2:
            chart_type_options = ["Biểu đồ cột (Top N)", "Biểu đồ tròn (Cơ cấu)", "Biểu đồ Treemap (Cơ cấu)", "Bảng dữ liệu (Chi tiết)"]
            selected_chart_type = st.selectbox("Chọn loại biểu đồ hiển thị:", options=chart_type_options, key="p1_chart_type_selector")
        
        # Filter out zero or null values
        df_page1_filtered = df_page1.dropna(subset=[selected_metric_col])
        df_page1_filtered = df_page1_filtered[df_page1_filtered[selected_metric_col] > 0]

        # Display charts
        if selected_chart_type == "Biểu đồ cột (Top N)":
            st.markdown(f"**Top Nông sản theo {selected_metric_label}**")
            df_bar = df_page1_filtered.sort_values(by=selected_metric_col, ascending=False)
            fig_bar = px.bar(df_bar, x="commodity", y=selected_metric_col, color="commodity", labels={'commodity': 'Nông sản', selected_metric_col: f'{selected_metric_label} ({selected_unit})'})
            fig_bar.update_xaxes(title_text='')
            st.plotly_chart(fig_bar, use_container_width=True)
        elif selected_chart_type == "Biểu đồ tròn (Cơ cấu)":
            st.markdown(f"**Cơ cấu {selected_metric_label}**")
            fig_pie = px.pie(df_page1_filtered, names="commodity", values=selected_metric_col, hole=0.3, labels={'commodity': 'Nông sản', selected_metric_col: f'{selected_metric_label} ({selected_unit})'})
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        elif selected_chart_type == "Biểu đồ Treemap (Cơ cấu)":
            st.markdown(f"**Cơ cấu {selected_metric_label} (Treemap)**")
            fig_treemap = px.treemap(df_page1_filtered, path=[px.Constant(f"Tất cả {selected_metric_label}"), 'commodity'], values=selected_metric_col, color='commodity', labels={'commodity': 'Nông sản', selected_metric_col: f'{selected_metric_label} ({selected_unit})'})
            fig_treemap.update_traces(textinfo="label+value+percent root")
            st.plotly_chart(fig_treemap, use_container_width=True)
        elif selected_chart_type == "Bảng dữ liệu (Chi tiết)":
            st.markdown(f"**Bảng dữ liệu chi tiết (đã xử lý)**")
            st.dataframe(df_page1_filtered[['commodity', 'season', 'area_thousand_ha', 'production_thousand_tonnes', 'yield_ta_per_ha']], use_container_width=True)
    else:
        st.warning("Không tìm thấy dữ liệu cho bộ lọc này.")


# --- TAB 2 CONTENT ---
with tab2:
    st.header("Phân tích Chuyên sâu (Trends & Comparisons)")
    
    with st.expander("💡 Xem hướng dẫn sử dụng bộ lọc (Slicer)", expanded=False):
        st.info("""
            Trang này cho phép bạn "cắt lớp" (slice) dữ liệu theo nhiều chiều. **Tất cả các bộ lọc bên dưới đều được áp dụng cùng lúc (lọc AND).**

            Bộ lọc **"So sánh theo"** (ở ngay bên dưới) là quan trọng nhất. Nó quyết định các đường màu trên biểu đồ sẽ đại diện cho cái gì.
            
            ---
            
            #### **Cách đọc biểu đồ:**

            **1. Khi bạn So sánh theo: "Khu vực"**
            * **Biểu đồ sẽ vẽ:** Một đường màu cho mỗi Vùng/Tỉnh bạn chọn trong bộ lọc "Lọc theo Không gian".
            * **Dữ liệu được tính:** Các bộ lọc "Nông sản" và "Mùa vụ" sẽ được áp dụng *chung* cho tất cả các khu vực đó.
            * **Ví dụ:** Lọc `Nông sản = [rice]`, `So sánh theo = Khu vực`, `Chọn Tỉnh = [An Giang, Vũng Tàu]` -> Biểu đồ sẽ so sánh sản lượng **Gạo của An Giang** với sản lượng **Gạo của Vũng Tàu**.

            **2. Khi bạn So sánh theo: "Nông sản"**
            * **Biểu đồ sẽ vẽ:** Một đường màu cho mỗi Nông sản bạn chọn trong bộ lọc "Lọc theo Dữ liệu".
            * **Dữ liệu được tính:** Các bộ lọc "Không gian" (Vùng/Tỉnh) sẽ được áp dụng *chung* (tính tổng).
            * **Ví dụ:** Lọc `Phân tích theo = province`, `Chọn Tỉnh = [An Giang, Vũng Tàu]`, `So sánh theo = Nông sản`, `Chọn Nông sản = [rice, maize]` -> Biểu đồ sẽ so sánh 2 đường:
                * Đường 1: **Tổng 'rice'** (của An Giang + Vũng Tàu)
                * Đường 2: **Tổng 'maize'** (của An Giang + Vũng Tàu)

            **3. Khi bạn So sánh theo: "Mùa vụ"**
            * **Biểu đồ sẽ vẽ:** Một đường màu cho mỗi Mùa vụ bạn chọn.
            * **Dữ liệu được tính:** Các bộ lọc "Không gian" và "Nông sản" sẽ được áp dụng *chung*.
            * **Ví dụ:** Lọc `Nông sản = [rice]`, `So sánh theo = Mùa vụ` -> Biểu đồ sẽ so sánh sản lượng Lúa vụ Đông Xuân, Hè Thu, v.v.
        """)

    # --- TAB 2 FILTERS ---
    with st.container(border=True):
        st.markdown("<h4 style='text-align: center; color: #FF4B4B;'>Yếu tố So sánh Chính (Quyết định màu sắc)</h4>", unsafe_allow_html=True)
        _col1, col_center, _col3 = st.columns([1, 1.5, 1])
        with col_center:
            compare_by_options = {"Khu vực": "region_name", "Nông sản": "commodity", "Mùa vụ": "season"}
            selected_color_label = st.selectbox("**So sánh theo:**", options=list(compare_by_options.keys()), key="p2_color_by")
            color_col = compare_by_options[selected_color_label]
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        # Filter for selecting spatial level (Region/Province/Country)
        """
        Region: 'Dong bang song Cuu Long', 'Dong Nam Bo', ...
        Province: 'An Giang', 'Ba Ria - Vung Tau', ...
        Country: Select nationwide (no additional selection needed)
        """
        with col1:
            st.markdown("#### 1. Lọc theo Không gian")
            selected_level_p2 = st.selectbox("Phân tích theo:", options=["country", "region", "province"], index=0, key="p2_level")
            if selected_level_p2 == "region":
                options = sorted(df_regions_master['region_name'].unique())
                selected_regions = st.multiselect("Chọn Vùng:", options, default=options[:2], key="p2_multi_region")
            else:
                selected_regions = [] 
            if selected_level_p2 == "province":
                options = sorted(df_provinces_master['province_name'].unique())
                selected_provinces = st.multiselect("Chọn Tỉnh (tối đa 10):", options, default=options[:5], max_selections=10, key="p2_multi_province")
            else:
                selected_provinces = []
        
        # Filter for selecting commodity type and season data (Commodity/Season)
        with col2:
            st.markdown("#### 2. Lọc theo Dữ liệu")
            options = sorted(df_agri_master['commodity'].unique())
            selected_commodities = st.multiselect("Chọn Nông sản:", options=options, default=options, key="p2_multi_commodity")
            options = sorted(df_agri_master['season'].dropna().unique())
            selected_seasons = st.multiselect("Chọn Mùa vụ:", options=options, default=options, key="p2_multi_season")
            st.info("Lọc theo mùa (trừ 'annual') chủ yếu áp dụng cho 'rice'.", icon="ℹ️")

        # Filter for selecting time range & metric (Year Range & Metric)
        with col3:
            st.markdown("#### 3. Lọc theo Thời gian & Chỉ số")
            min_year = int(df_agri_master['year'].min())
            max_year = int(df_agri_master['year'].max())
            selected_year_range = st.slider("Chọn khoảng năm:", min_value=min_year, max_value=max_year, value=(min_year, max_year), step=1, key="p2_year_range")
            metric_options = {"Sản lượng": "production_thousand_tonnes", "Diện tích": "area_thousand_ha", "Năng suất": "yield_ta_per_ha"}
            selected_metric_label = st.selectbox("Chọn chỉ số:", options=list(metric_options.keys()), key="p2_metric")
            selected_metric_col = metric_options[selected_metric_label]
            units = {"production_thousand_tonnes": "Nghìn Tấn", "area_thousand_ha": "Nghìn Ha", "yield_ta_per_ha": "Tạ/Ha"}
            selected_unit = units[selected_metric_col]
            
    # -- FILTER DATA FOR TAB 2 --
    df_page2 = df_agri_master.copy()
    df_page2 = df_page2[(df_page2['year'] >= selected_year_range[0]) & (df_page2['year'] <= selected_year_range[1])]
    df_page2 = df_page2[df_page2['region_level'] == selected_level_p2]
    if selected_regions:
        df_page2 = df_page2[df_page2['region_name'].isin(selected_regions)]
    if selected_provinces:
        df_page2 = df_page2[df_page2['region_name'].isin(selected_provinces)]
    if selected_commodities:
        df_page2 = df_page2[df_page2['commodity'].isin(selected_commodities)]
    if selected_seasons:
        df_page2 = df_page2[df_page2['season'].isin(selected_seasons)]

    # -- DISPLAY TAB 2 CONTENT --
    if not df_page2.empty:
        # --- Handle Null values (similar to tab 1) ---
        df_page2['production_thousand_tonnes'] = pd.to_numeric(df_page2['production_thousand_tonnes'], errors='coerce')
        df_page2['area_thousand_ha'] = pd.to_numeric(df_page2['area_thousand_ha'], errors='coerce')
        df_page2['yield_ta_per_ha'] = pd.to_numeric(df_page2['yield_ta_per_ha'], errors='coerce')
        mask_yield = df_page2['yield_ta_per_ha'].isnull() & df_page2['production_thousand_tonnes'].notnull() & df_page2['area_thousand_ha'].notnull() & (df_page2['area_thousand_ha'] > 0)
        df_page2.loc[mask_yield, 'yield_ta_per_ha'] = (df_page2['production_thousand_tonnes'] / df_page2['area_thousand_ha']) * 10
        
        st.markdown("---")
        st.subheader(f"So sánh {selected_metric_label} (So sánh theo: {selected_color_label})")
        
        # Group data by 'year' and 'color_col'
        df_trend = df_page2.dropna(subset=[color_col])
        df_trend = df_trend.groupby(['year', color_col])[selected_metric_col].sum().reset_index()
        
        if df_trend.empty:
            st.warning("Không tìm thấy dữ liệu sau khi nhóm. Hãy thử thay đổi bộ lọc.")
        else:
            # CHART 1: Multi-Line Chart
            fig_trend = px.line(df_trend, x='year', y=selected_metric_col, color=color_col, title=f"Xu hướng {selected_metric_label} qua các năm", markers=True, labels={'year': 'Năm', selected_metric_col: f'{selected_metric_label} ({selected_unit})', color_col: selected_color_label})
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # CHART 2: Grouped Bar Chart
            st.subheader(f"Phân tích chi tiết từng năm")
            fig_bar_grouped = px.bar(df_trend, x='year', y=selected_metric_col, color=color_col, barmode='group', title=f"So sánh {selected_metric_label} hàng năm", labels={'year': 'Năm', selected_metric_col: f'{selected_metric_label} ({selected_unit})', color_col: selected_color_label})
            st.plotly_chart(fig_bar_grouped, use_container_width=True)
            
            # CHART 3: Stacked Area Chart (100%)
            st.markdown("---")
            st.subheader(f"Phân tích Cơ cấu {selected_metric_label} (100%)")
            fig_area = px.area(df_trend, x='year', y=selected_metric_col, color=color_col, groupnorm='percent', title=f"Sự thay đổi Cơ cấu {selected_metric_label} qua các năm", labels={'year': 'Năm', selected_metric_col: f'Cơ cấu {selected_metric_label} (%)', color_col: selected_color_label})
            st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.warning("Không tìm thấy dữ liệu cho bộ lọc này.")
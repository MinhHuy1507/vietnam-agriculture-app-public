"""
File: pages/2_Phân_tích_Địa_lý.py
Description:
    This is the "Geographic Analysis" page of the application.
    This page is responsible for:
    1. Retrieving data.
    2. Manually defining coordinates (lon, lat) for Vietnam's economic regions.
    3. Defining "jitter map" and color scheme for each commodity type.
    4. Providing filters (by Year, Metric, Commodity) for the map.
    5. Processing logic to "flatten" data, assign coordinates and colors.
    6. Rendering 3D map (PyDeck ColumnLayer) to display multiple 3D columns (for multiple commodities)
    at each region.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk 

from utils.load_data import load_master_data

# --- 1. RETRIEVE DATA ---
df_agri_master, df_provinces_master, df_regions_master, df_climate_master, df_soil_master = load_master_data()

# --- 2. CENTER COORDINATES FOR REGIONS ---
REGION_COORDS = {
    "Dong bang song Hong": {"lon": 105.9700701, "lat": 20.9038458},
    "Trung du va mien nui phia Bac": {"lon": 104.6583622, "lat": 21.5824578},
    "Bac Trung Bo va Duyen hai mien Trung": {"lon": 105.9709102, "lat": 17.9481570},
    "Tay Nguyen": {"lon": 108.2376892, "lat": 13.0653077},
    "Dong Nam Bo": {"lon": 106.9122119, "lat": 11.2193217},
    "Dong bang song Cuu Long": {"lon": 105.5996987, "lat": 10.0718802}
}
df_region_coords = pd.DataFrame.from_dict(REGION_COORDS, orient='index', columns=['lon', 'lat'])
df_region_coords = df_region_coords.reset_index().rename(columns={'index': 'region_name'})

# --- 3. JITTER MAP AND COLOR SCHEME ---
COMMODITY_VISUALS = {
    "rice":         {'off_lon': 0.0,  'off_lat': 0.0,  'color': [0, 128, 255]},
    "maize":        {'off_lon': 0.3,  'off_lat': 0.0,  'color': [255, 255, 0]},
    "cassava":      {'off_lon': -0.3, 'off_lat': 0.0,  'color': [139, 69, 19]},
    "sweet_potato": {'off_lon': 0.0,  'off_lat': 0.3,  'color': [255, 165, 0]},
    "sugarcane":    {'off_lon': 0.3,  'off_lat': 0.3,  'color': [0, 255, 0]},
    "groundnut":    {'off_lon': -0.3, 'off_lat': -0.3, 'color': [255, 0, 0]}
}
df_comm_visuals = pd.DataFrame.from_dict(COMMODITY_VISUALS, orient='index')
df_comm_visuals = df_comm_visuals.reset_index().rename(columns={'index': 'commodity'})

# --- 4. PAGE 2 CONTENT: 3D MAP BY REGION ---
st.title("🗺️ Phân tích Địa lý (Bản đồ Vùng 3D)")
st.markdown("Trực quan hóa dữ liệu nông nghiệp theo các Vùng Kinh tế trên bản đồ 3D.")
st.info("Bản đồ nền (Sáng/Tối) được tự động chọn theo cài đặt Theme của Streamlit.", icon="💡")

# --- PAGE 2 SPECIFIC FILTERS ---
st.subheader("Bộ lọc Dữ liệu Bản đồ")
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    
    # Year filter
    with col1:
        min_year = int(df_agri_master['year'].min())
        max_year = int(df_agri_master['year'].max())
        selected_year_p3 = st.slider(
            "Chọn Năm:", min_value=min_year, max_value=max_year,
            value=max_year, step=1, key="p3_year"
        )

    # Metric filter
    with col2:
        metric_options = {
            "Sản lượng": "production_thousand_tonnes",
            "Diện tích": "area_thousand_ha",
            "Năng suất": "yield_ta_per_ha"
        }
        selected_metric_label = st.selectbox(
            "Chọn chỉ số:", options=list(metric_options.keys()),
            key="p3_metric"
        )
        selected_metric_col = metric_options[selected_metric_label]
        units = {"production_thousand_tonnes": "Nghìn Tấn", "area_thousand_ha": "Nghìn Ha", "yield_ta_per_ha": "Tạ/Ha"}
        selected_unit = units[selected_metric_col]

    # Multi-commodity selection filter
    with col3:
        commodity_list = sorted(df_agri_master['commodity'].unique())
        selected_commodities_p3 = st.multiselect(
            "Chọn Nông sản:", 
            options=commodity_list, 
            default=commodity_list
        )

# --- FILTER DATA FOR PAGE 2 ---
# 1. Filter by user selections
df_page3 = df_agri_master.copy()
df_page3 = df_page3[
    (df_page3['year'] == selected_year_p3) &
    (df_page3['region_level'] == 'region') 
]
if selected_commodities_p3:
    df_page3 = df_page3[df_page3['commodity'].isin(selected_commodities_p3)]
else:
    st.warning("Vui lòng chọn ít nhất 1 loại nông sản.")
    st.stop()

# 2. Handle Null values
"""
    Some records are missing one of three metrics: production, area, yield.
    Apply formula to calculate missing metric when possible.
    yield (quintals/ha) = production (1000 tonnes) / area (1000 ha) * 10
"""
df_page3['production_thousand_tonnes'] = pd.to_numeric(df_page3['production_thousand_tonnes'], errors='coerce')
df_page3['area_thousand_ha'] = pd.to_numeric(df_page3['area_thousand_ha'], errors='coerce')
df_page3['yield_ta_per_ha'] = pd.to_numeric(df_page3['yield_ta_per_ha'], errors='coerce')

mask_yield = df_page3['yield_ta_per_ha'].isnull() & df_page3['production_thousand_tonnes'].notnull() & df_page3['area_thousand_ha'].notnull() & (df_page3['area_thousand_ha'] > 0)
df_page3.loc[mask_yield, 'yield_ta_per_ha'] = (df_page3['production_thousand_tonnes'] / df_page3['area_thousand_ha']) * 10

mask_prod = df_page3['production_thousand_tonnes'].isnull() & df_page3['yield_ta_per_ha'].notnull() & df_page3['area_thousand_ha'].notnull()
df_page3.loc[mask_prod, 'production_thousand_tonnes'] = (df_page3['yield_ta_per_ha'] * df_page3['area_thousand_ha']) / 10

mask_area = df_page3['area_thousand_ha'].isnull() & df_page3['yield_ta_per_ha'].notnull() & df_page3['production_thousand_tonnes'].notnull() & (df_page3['yield_ta_per_ha'] > 0)
df_page3.loc[mask_area, 'area_thousand_ha'] = (df_page3['production_thousand_tonnes'] / df_page3['yield_ta_per_ha']) * 10

# 3. Group by Region and Commodity
df_map_data_calculated = df_page3.groupby(['region_name', 'commodity'])[selected_metric_col].sum().reset_index()

# 4. Merge 3 tables: (Calculated Data) + (Region Coordinates) + (Color & Jitter)
df_map_data = pd.merge(
    df_region_coords, df_map_data_calculated, on='region_name', how='inner'
)
df_map_data = pd.merge(
    df_map_data, df_comm_visuals, on='commodity', how='left'
).fillna(0)

# 5. Create final coordinates
df_map_data['lon_jittered'] = df_map_data['lon'] + df_map_data['off_lon']
df_map_data['lat_jittered'] = df_map_data['lat'] + df_map_data['off_lat']


# --- DISPLAY PAGE 2 CONTENT (PYDECK) ---
st.markdown("---")
st.subheader(f"Bản đồ 3D {selected_metric_label} các Vùng (Năm {selected_year_p3})")

df_pydeck = df_map_data[df_map_data[selected_metric_col] > 0]

if not df_pydeck.empty:
    # Create formatted tooltip column to fix PyDeck display issue
    df_pydeck['tooltip_metric'] = df_pydeck[selected_metric_col].apply(lambda x: f"{x:,.2f}")
    
    # Dynamically calculate scale for column height
    max_value = df_pydeck[selected_metric_col].max()
    if max_value == 0: max_value = 1 
    
    DESIRED_MAX_HEIGHT_METERS = 500000 
    dynamic_elevation_scale = DESIRED_MAX_HEIGHT_METERS / max_value
    
    view_state = pdk.ViewState(
        latitude=16.047079, longitude=108.206230, zoom=4.5, pitch=50 
    )
    layer = pdk.Layer(
        "ColumnLayer",
        data=df_pydeck,
        get_position=['lon_jittered', 'lat_jittered'],
        get_elevation=selected_metric_col,
        get_fill_color='color',
        elevation_scale=dynamic_elevation_scale, 
        radius=15000, 
        pickable=True,
        auto_highlight=True,
    )
    tooltip = {
        "html": (
            "<b>{region_name}</b><br/>"
            "<b>Nông sản:</b> {commodity}<br/>"
            f"<b>{selected_metric_label}:</b> {{tooltip_metric}} {selected_unit}" 
        ),
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=None, 
        tooltip=tooltip
    )
    st.pydeck_chart(deck)
    
else:
    st.warning("Không tìm thấy dữ liệu cho bộ lọc này.")
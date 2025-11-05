# Frontend Documentation: Page-by-Page Breakdown

This document details the features, user interactions, and data logic for each page within the Streamlit application.

* **Main Application File:** `Trang_chu.py`
* **Sub-Pages:** Located in the `pages/` directory.

---

## 🏠 Trang chủ (Home)
* **File:** `Trang_chu.py`
* **Purpose:** Serves as the main entry point and navigation hub.
* **Key Logic:**
    1.  **Navigation:** Uses `st.navigation` to create the sidebar menu, defining the title, icon, and file path for all other pages.
    2.  **Content:** Displays a static welcome message and project overview.

## 1. 📊 Phân tích Nông nghiệp
* **File:** `pages/1_Phân_tích_Nông_nghiệp.py`
* **Purpose:** Provides a comprehensive analysis of the core agricultural data (production, area, yield).
* **Structure:** Organized into two tabs for different analysis depths.

### Tab 1: Tổng quan (Snapshot)
* **User Story:** "As a user, I want to see a high-level snapshot of all agricultural metrics for a **single year** and a **single region/commodity**."
* **Filters:**
    * `st.selectbox` for Level (country, region, province).
    * `st.selectbox` for Region/Province (dynamically disabled).
    * `st.slider` for selecting a *single* year.
    * `st.selectbox` for selecting a *single* commodity or "Tất cả".
* **Visualizations:**
    * **KPI Metrics:** Three `st.metric` cards showing total Production, Area, and average Yield for the filtered data.
    * **Chart Filters:** User can select a metric (e.g., "Sản lượng") and a chart type (e.g., "Biểu đồ cột").
    * **Dynamic Charts:** Renders one of four Plotly charts based on user selection:
        * `px.bar` (Top N)
        * `px.pie` (Donut Chart)
        * `px.treemap`
        * `st.dataframe` (Raw data)
* **Data Logic:**
    * Loads data from `st.session_state`.
    * Applies "Phương pháp 2" (calculating missing `yield`/`production`/`area` from the other two) to the filtered DataFrame *before* displaying KPIs or charts.

### Tab 2: Phân tích Chuyên sâu (Trends & Comparisons)
* **User Story:** "As a user, I want to **compare multiple items** (e.g., different crops, different regions) against each other **over a period of time**."
* **Filters (Slicers):**
    * `st.selectbox` for **"So sánh theo" (Color By):** The most important filter. It defines what the colors on the chart represent (Khu vực, Nông sản, or Mùa vụ).
    * `st.slider` for selecting a *range* of years (e.g., 1995-2024).
    * `st.multiselect` for "Chọn Vùng", "Chọn Tỉnh" (max 10), "Chọn Nông sản", "Chọn Mùa vụ".
* **Visualizations:**
    * **Multi-Line Chart (`px.line`):** Shows the trend of the selected items over time.
    * **Grouped Bar Chart (`px.bar(barmode='group')`):** Allows for year-by-year comparison of the selected items.
    * **Stacked Area Chart (`px.area(groupnorm='percent')`):** Shows the change in *composition* (market share) of the selected items over time.
* **Data Logic:**
    * Applies all filters (slicers) to the master data.
    * Groups the data by `year` and the chosen `color_col` (e.g., `commodity`).
    * Calculates the `sum()` of the selected metric (`selected_metric_col`).
    * This aggregated DataFrame is then fed into all three charts.

## 2. 🗺️ Phân tích Địa lý (Provinces)
* **File:** `pages/2_Phân_tích_Địa_lý.py`
* **Purpose:** To visualize the geographical distribution of agricultural data by *economic region*.
* **Filters:**
    * `st.slider` for a *single* year.
    * `st.selectbox` for a metric (Sản lượng, Diện tích, Năng suất).
    * `st.multiselect` to select one or more "Nông sản".
* **Visualization:** **3D Column Map (`st.pydeck_chart`)**.
* **Data Logic:**
    1.  Hardcoded dictionary (`REGION_COORDS`) maps the 6 economic regions to specific `(lon, lat)` coordinates.
    2.  Hardcoded dictionary (`COMMODITY_VISUALS`) maps each commodity to a color `[R,G,B]` and a coordinate "jitter" (offset).
    3.  Data is filtered by the user's selections and grouped by `region_name` and `commodity`.
    4.  The `COMMODITY_VISUALS` are merged in to create "jittered" coordinates (`lon_jittered`) and assign a `color` column.
    5.  A dynamic `elevation_scale` is calculated to ensure both high-value (Production) and low-value (Yield) metrics are visible.
    6.  A PyDeck `ColumnLayer` is rendered using these jittered coordinates, dynamic heights, and custom colors.

## 3. ☀️ Phân tích Khí hậu (Climate)
* **File:** `pages/3_Phân_tích_Khí_hậu.py`
* **Purpose:** To analyze climate trends and their correlation with agricultural performance.
* **Structure:** Two tabs.

### Tab 1: Phân tích Xu hướng Khí hậu
* **User Story:** "As a user, I want to see how all climate indicators for a **single province** have changed over time."
* **Filters:** `st.selectbox` for Province, `st.slider` for year range.
* **Visualizations:** A series of `px.line` and `px.bar` charts showing trends for all 10+ climate indicators (Temperature, Precipitation, Pressure, etc.).

### Tab 2: Phân tích Tương quan
* **User Story:** "As a user, I want to see if a **climate indicator** (e.g., Rain) has a relationship with an **agricultural indicator** (e.g., Yield) in a specific province."
* **Filters:** Select Province, Agri-metric (Y-axis), and Climate-metric (X-axis).
* **Visualizations:**
    * **Dual-Axis Chart (`make_subplots`):** A Bar chart (Agri) and Line chart (Climate) overlaid to show correlation over time.
    * **Scatter Plot (`px.scatter`):** Shows the direct relationship between the two metrics, with an "ols" trendline (`trendline="ols"`) to show statistical correlation.

## 4. 🌱 Phân tích Thổ nhưỡng (Soil)
* **File:** `pages/4_Phân_tích_Thổ_nhưỡng.py`
* **Purpose:** To analyze soil quality data (from GEE) and its correlation with agricultural performance.
* **Structure:** Two tabs.

### Tab 1: Phân bố Thổ nhưỡng
* **User Story:** "As a user, I want to **rank all provinces** based on a specific soil quality metric."
* **Filters:** `st.selectbox` to choose one soil metric (e.g., pH, Nitrogen %, Sand %).
* **Visualizations:** A `px.bar` chart ranking all provinces by the selected metric.

### Tab 2: Tương quan (Đất & Nông nghiệp)
* **User Story:** "As a user, I want to see if **soil quality** (e.g., Organic Carbon %) has a relationship with average agricultural performance in that province."
* **Filters:** Select Agri-metric (Y-axis, *averaged over all years*), Soil-metric (X-axis), and Commodity.
* **Data Logic:**
    1.  Calculates the *mean* (trung bình) of the selected agri-metric for each province across all years.
    2.  Merges this average with the static soil data.
* **Visualizations:** A `px.scatter` plot with an "ols" trendline to show the relationship.

## 5. 🔮 Dự đoán Số liệu
* **File:** `pages/5_Dự_đoán_số_liệu.py`
* **Purpose:** Provides a UI to interact with the (currently mocked) ML prediction model.
* **Structure:** A hybrid UI using `st.form`.
* **Data Logic:**
    1.  **Outside Form:** User selects basic filters (Province, Commodity, Year, Season). The page *reacts* instantly to `st.selectbox("Chọn Tỉnh:")`.
    2.  **Auto-fill:** When the province changes, the app automatically fetches and displays the 7 static **Soil features** for that province (using `st.metric`).
    3.  **Inside Form:** User enters 10 variable **Climate features** (e.g., forecasted temperature).
    4.  **On Submit:**
        * The 4 basic features + 7 static soil features + 10 climate features are combined into a 21-feature JSON payload.
        * (Imputation: If a climate feature is left at `0`, the app uses the historical average for that province).
        * A `requests.post` call is made to the `POST /api/v1/predict` endpoint.
        * The returned JSON (`predicted_production`, `predicted_area`, `predicted_yield`) is displayed in `st.metric` cards.    
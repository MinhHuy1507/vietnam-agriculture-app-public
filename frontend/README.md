# Frontend: Vietnam Agriculture Dashboard (Streamlit)

This directory contains the Streamlit application that serves as the visual, interactive frontend for the Vietnam Agriculture Analytics project.

It is a multi-page application designed to consume data from the FastAPI backend and present it to the end-user through a series of specialized dashboards.

* **Live Dashboard:** [vietnam-agri-app-public.streamlit.app](https://vietnam-agriculture-app-public.streamlit.app/)
* **Root README:** [Return to Main Project](../README.md)

---

## 1. Technology Stack

* ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white): Core framework for building the web application.
* ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white): Used for all 2D interactive charts (Line, Bar, Pie, Treemap, Scatter).
* ![PyDeck](https://img.shields.io/badge/deck.gl-000000?style=for-the-badge&logo=deckdotgl&logoColor=white): Used for 3D geospatial mapping (ColumnLayer) on the geography page.
* ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white): Used for all data manipulation, filtering, and processing (like calculating `yield`) on the client-side.
* ![Requests](https://img.shields.io/badge/Requests-222222?style=for-the-badge): Used to make HTTP calls to the backend API.

## 2. Project Structure (Multi-Page App)

This app uses Streamlit's native Multi-Page App architecture, which is defined by the file structure:

```
frontend/
│
├── pages/                    # Contains all sub-pages
│   ├── 1_Phan_tich_Nong_nghiep.py
│   ├── 2_Phan_tich_Dia_ly.py
│   ├── 3_Phan_tich_Khi_hau.py
│   ├── 4_Phan_tich_Tho_nhuong.py
│   └── 5_Du_doan.py
│
├── utils/
│   ├── __init__.py
│   └── load_data.py          # Central utility for all data loading logic
│
├── README.md                 # `This file`
├── .dockerignore             # Ignores venv, pycache for Docker builds
├── Dockerfile                # Instructions to build the frontend image
├── Trang_chu.py              # Main entrypoint, handles navigation & home page
└── requirements.txt          # Python dependencies
```

* **`Trang_chu.py`**: This is the main entrypoint. It defines the `st.navigation` menu, sets the app configuration (`st.set_page_config`), and contains the code for the "Trang chủ" (Home) page.
* **`utils/load_data.py`**: This is the central utility module. It contains the `load_all_data_from_api` function (which handles API calls and pagination) and the `load_master_data` function (which loads all data into a `@st.cache_data` object).
* **`pages/`**: Each file in this directory automatically becomes a page in the sidebar navigation. Each page imports `load_master_data` from the `utils` file to get its data, ensuring data is loaded independently and correctly, even on a page refresh.

## 3. Data Flow & API Connection

This frontend is a "dumb client"—it does not connect to the database. It relies entirely on the FastAPI backend.

1.  **API URL:** The app reads the backend's address from an environment variable `API_BASE_URL`.
    * **Production (Streamlit Cloud):** This is set in the **Secrets** (e.g., `API_BASE_URL = "https://...onrender.com/api/v1"`).
    * **Local (Docker Compose):** This is set in `docker-compose.yml` (e.g., `API_BASE_URL = "http://backend:8000/api/v1"`).
    * **Local (Standalone):** It defaults to `http://localhost:8000/api/v1`.

2.  **Data Loading:**
    * The `load_all_data_from_api` function in `utils/load_data.py` calls the backend endpoints (e.g., `/statistics/agriculture-data`).
    * It handles the API's pagination by looping (`while True`) and fetching 1000 records at a time until all data is retrieved.

3.  **Caching:**
    * `@st.cache_data(ttl=600)` is used heavily to cache the results of API calls (master data) for 10 minutes. This means the API is only called once when the app starts, providing near-instant page loads and filter responses.

## 4. Local Development (Standalone)

You can run the Streamlit app without Docker, *as long as the backend API is running* (either via Docker or locally).

1.  **Set up a Virtual Environment:**
    ```bash
    cd ./frontend
    python -m venv frontend_venv
    .\frontend_venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App:**
    * (Make sure the API is running on `http://localhost:8000`)
    ```bash
    streamlit run Trang_chu.py
    ```
    The app will be available at `http://localhost:8501`.
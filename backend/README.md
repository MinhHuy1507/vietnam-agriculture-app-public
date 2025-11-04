# Backend: Vietnam Agriculture API (FastAPI)

This directory contains the FastAPI application that serves as the primary backend for the Vietnam Agriculture Analytics project.

It is responsible for connecting to the PostgreSQL database, executing queries, processing data, and exposing clean RESTful API endpoints for the Streamlit frontend to consume.

* **Live API Docs:** [FastAPI/docs](https://vietnam-agriculture-app-public-backend.onrender.com/docs)
* **Root README:** [Return to Main Project](../README.md)

---

## 1. Technology Stack

* ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white): Core web framework for building the API.
* ![SQLModel](https://img.shields.io/badge/SQLModel-48B0F0?style=for-the-badge&logo=python&logoColor=white): Used as the ORM (for database queries) and for data validation (Pydantic).
* ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white): The production database storing all cleaned data.
* ![Uvicorn](https://img.shields.io/badge/Uvicorn-27A7E7?style=for-the-badge&logo=python&logoColor=white): ASGI server used to run FastAPI.
* ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white): Core programming language.

## 2. Project Structure

The backend code is organized into logical, decoupled files:

```
backend/
│
├── data/                     # CSV data files used for database seeding
│   ├── agriculture.csv
│   ├── climate.csv
│   ├── province.csv
│   └── soil.csv
│
├── utils/
│   └── connect_database.py   # Manages DB connection (engine, session)
│
├── .dockerignore             # Ignores venv, pycache for Docker builds
├── Dockerfile                # Instructions to build the backend image
├── dependencies.py           # Pydantic models for API Query Params & Enums
├── main.py                   # Main FastAPI app: defines all API endpoints
├── model.py                  # SQLModel schemas for Database Tables (DB Models)
├── requirements.txt          # Python dependencies
├── schemas.py                # Pydantic schemas for API Responses (Read Models)
├── README.md                 # `This file`
└── seed_db.py                # Standalone script to reset and populate the DB
```

## 3. Database Schema

The database is normalized into four primary tables, defined in `model.py`:

1.  **`Province`**: Dimension table holding static data for 63 provinces (coordinates, names).
2.  **`AgricultureData`**: Main fact table containing time-series data for production, area, and yield. Includes data for `province`, `region`, and `country` levels.
3.  **`ClimateData`**: Fact table holding time-series climate data, linked to `Province` via a foreign key.
4.  **`SoilData`**: Fact table holding static soil data (pH, nitrogen, etc.), linked to `Province` via a foreign key.

## 4. API Endpoints

All data endpoints are under the `/api/v1/` prefix.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Welcome message for the API root. |
| `GET` | `/db-test` | Utility endpoint to check database connection status. |
| `GET` | `/api/v1/statistics/provinces` | Retrieves a list of all 63 provinces. |
| `GET` | `/api/v1/statistics/agriculture-data`| Retrieves agricultural data with optional filters (year, commodity, season, etc.). |
| `GET` | `/api/v1/statistics/climate-data` | Retrieves climate data, joined with province names. |
| `GET` | `/api/v1/statistics/soil-data` | Retrieves soil data, joined with province names. |
| `POST`| `/api/v1/predict` | **(Mocked)** Receives 21 input features and returns a mocked prediction for production, area, and yield. |

For detailed request/response models, see the live [FastAPI/docs](https://vietnam-agriculture-app-public-backend.onrender.com/docs)

## 5. Local Development (Standalone)

While `docker-compose` (in the root directory) is the recommended way to run this project, you can also run the backend as a standalone service.

1.  **Set up a Virtual Environment:**
    ```bash
    cd ./backend
    python -m venv backend_venv
    .\backend_venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Environment Variables:**
    * The API connects to the database using environment variables defined in `utils/connect_database.py`. You must set these in your terminal for the API to connect:
    ```bash
    # Example for PowerShell (Windows)
    $env:DB_HOST = "localhost"
    $env:DB_PORT = "5433" # Port mapped in docker-compose
    $env:DB_USER = "vietnamagriculture"
    $env:DB_PASS = "vietnamagriculture"
    $env:DB_NAME = "vietnam_agriculture"
    ```

4.  **Run the Seeder (One time):**
    * (Requires a running PostgreSQL instance at the address above)
    ```bash
    python seed_db.py
    ```

5.  **Run the Server:**
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.
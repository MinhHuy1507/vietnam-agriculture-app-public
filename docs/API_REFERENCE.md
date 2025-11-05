# API Reference Guide

This document provides a detailed reference for all available API endpoints, supplementing the auto-generated.

* **Base URL (Production):** [FastAPI/docs](https://vietnam-agriculture-app-public-backend.onrender.com/docs)
* **Base URL (Local):** `http://localhost:8000`

All data endpoints are prefixed with `/api/v1/`.

---

## Authentication (Xác thực)

All `GET` endpoints on this API are public and do not require authentication.

---

## Data Endpoints (GET)

These endpoints are used by the dashboard to fetch data for visualization. They all support standard pagination via `skip` (int) and `limit` (int) query parameters.

### `GET /api/v1/statistics/agriculture-data`

Retrieves time-series agricultural data (area, production, yield).

**Query Parameters (based on `AgricultureQuery`):**
* `year: Optional[str]`: Filters by a specific year.
* `commodity: Optional[Commodity]` (Enum): Filters by a specific commodity (e.g., `rice`, `maize`).
* `season: Optional[Season]` (Enum): Filters by a specific season (e.g., `winter_spring`).
* `region_name: Optional[str]`: Filters by the specific name (e.g., "An Giang", "Dong bang song Cuu Long").
* `region_level: Optional[RegionLevel]` (Enum): Filters by level (`province`, `region`, `country`).

### `GET /api/v1/statistics/climate-data`

Retrieves time-series climate data for all provinces. This endpoint automatically performs a `JOIN` with the `Province` table to include `province_name` in the response.

**Query Parameters (based on `ClimateQuery`):**
* `year: Optional[str]`: Filters by a specific year.
* `province_name: Optional[str]`: Filters for a single province name.

### `GET /api/v1/statistics/soil-data`

Retrieves static soil data for all provinces. This endpoint automatically performs a `JOIN` with the `Province` table to include `province_name` in the response.

**Query Parameters:**
* (None)

### `GET /api/v1/statistics/provinces`

Retrieves a static list of all 63 provinces and their geographic metadata (coordinates).

**Query Parameters:**
* (None)

---

## Prediction Endpoint (POST)

This is the primary machine learning endpoint used by the "Dự đoán" page.

### `POST /api/v1/predict`

Receives a JSON body containing 21 input features and returns a mocked (or real, if model is plugged in) prediction for `production`, `area`, and `yield`.

**Request Body Schema (`PredictionInput`):**
The API expects a JSON object with the following 21 keys.

**JSON Payload Example:**
```json
{
  "province_name": "An Giang",
  "year": 2025,
  "commodity": "rice",
  "season": "winter_spring",
  
  "avg_temperature": 27.5,
  "min_temperature": 15.0,
  "max_temperature": 40.0,
  "surface_temperature": 28.0,
  "wet_bulb_temperature": 25.0,
  "precipitation": 5.3,
  "solar_radiation": 19.1,
  "relative_humidity": 77.0,
  "wind_speed": 2.5,
  "surface_pressure": 100.9,
  
  "surface_elevation": 4.0,
  "avg_ndvi": 0.565,
  "soil_ph_level": 5.7,
  "soil_organic_carbon": 1.93,
  "soil_nitrogen_content": 0.2296,
  "soil_sand_ratio": 21.1,
  "soil_clay_ratio": 42.3
}
```

**Response Body Schema (`PredictionOutput`):**
The API returns a JSON object with the three predicted values.

**JSON Response Example:**
```json
{
  "predicted_production": 5432.1,
  "predicted_area": 890.5,
  "predicted_yield": 61.0
}
```

---
**[Return to Main Project README](../README.md)**
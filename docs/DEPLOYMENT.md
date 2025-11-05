# Deployment Strategy

This document details the production deployment strategy for the `vietnam-agri-app` project. While `docker-compose.yml` is used for a unified local development environment, the production environment utilizes a decoupled, multi-platform approach to leverage the best of free-tier cloud services.

**Key Strategy:** Deploy the **Backend (API)** and **Frontend (Dashboard)** as two separate, independent services on two different platforms.

* **Backend (FastAPI + PostgreSQL):** Deployed on **[Render.com](https://render.com/)**.
* **Frontend (Streamlit):** Deployed on **[Streamlit Community Cloud](https://share.streamlit.io/)**.

---

## Part 1: Backend & Database Deployment (Render.com)

The backend consists of two components on Render: the **PostgreSQL Database** (to hold the data) and the **Web Service** (to run the FastAPI API).

### 1.1. Why Render?

* **Free Tier:** Render's free tier provides both a PostgreSQL database and a Web Service, which is sufficient for a portfolio project.
* **Persistent Storage:** The PostgreSQL service provides persistent storage for the data.
* **CI/CD from Git:** Automatically deploys new code when a `git push` is made to the main branch.
* **Internal Networking:** Allows the API (`Web Service`) to communicate securely with the Database (`PostgreSQL`) over a private network.

### 1.2. Deployment Steps

#### Step 1: Deploy the Database (PostgreSQL)

1.  Create a new **"PostgreSQL"** service on Render.
2.  Provide a name (e.g., `vietnam-agri-db`), database name (e.g., `vietnam_agriculture`), and user (e.g., `vietnamagriculture`).
3.  Select the **"Free"** plan.
4.  Set the **Region** to `Singapore (Southeast Asia)` for the lowest latency.
5.  After creation, navigate to the "Connections" tab and copy the **Internal Connection String** (or Host, User, Pass, DB Name).

*Note: The Render free-tier PostgreSQL database is automatically deleted after 90 days of inactivity.*

#### Step 2: Deploy the API (Web Service)

1.  Create a new **"Web Service"** and connect the `agri-app-public` GitHub repository.
2.  Set the following configurations:
    * **Name:** `vietnam-agri-backend`
    * **Root Directory:** `./backend` (This is critical, as it tells Render to only look inside the `backend/` folder).
    * **Environment:** `Python 3`
    * **Build Command:** `pip install -r requirements.txt`
    * **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000` (Render's free web services require binding to port 10000).

#### Step 3: Set Environment Variables

1.  In the `vietnam-agri-backend` service's **"Environment"** tab, add the following environment variables (using the credentials from Step 1):
    * `DB_HOST`: The host from Render's "Connections" tab.
    * `DB_USER`: The user for the Render database.
    * `DB_PASS`: The password for the Render database.
    * `DB_NAME`: The name of the Render database.
    * `DB_PORT`: `5432` (This is the internal port).
2.  The `backend/utils/connect_database.py` script is designed to read these variables automatically.

#### Step 4: Run the Database Seeder (One-off Job)

1.  The database is currently empty. We must run the `seed_db.py` script once.
2.  Navigate to the `vietnam-agri-backend` service's **"Settings"** tab.
3.  Temporarily change the **"Start Command"** from `uvicorn...` to `python seed_db.py`.
4.  Save changes. This will trigger a new deploy.
5.  Go to the **"Logs"** tab and monitor the deployment. You will see the script output (e.g., "Inserting provinces data...").
6.  Wait for the log to show `🎉 Quá trình nạp dữ liệu mồi hoàn tất!`.
7.  **Crucially:** Go back to **"Settings"** and change the **"Start Command"** *back* to `uvicorn main:app --host 0.0.0.0 --port 10000`.
8.  Save changes again. The service will restart, this time as a live API server.

**Result:** The backend is now live at its public URL (e.g., `https://vietnam-agri-backend.onrender.com`).

---

## Part 2: Frontend Deployment (Streamlit Community Cloud)

### 2.1. Why Streamlit Cloud?

* It is 100% free for public repositories.
* It is perfectly optimized for hosting Streamlit applications.
* It provides one-click deployment and CI/CD from GitHub.

### 2.2. The "Refresh" Problem & Refactor

A critical architectural challenge with Streamlit Cloud is that it does **not** support `st.session_state` persistence on page refresh in the same way `docker-compose` does. Our initial design (loading all data in `Trang_chủ.py` and storing it in `st.session_state`) would fail with a `KeyError` whenever a user refreshed a sub-page.

**Solution:**
The application was refactored so that **each page is responsible for its own data loading**.
1.  A central utility file (`frontend/utils/load_data.py`) was created, containing the master data-loading functions (`load_master_data`, `load_all_data_from_api`).
2.  The main `Trang_chủ.py` file was simplified to *only* handle navigation (`st.navigation`).
3.  Every file in the `pages/` directory now starts by importing and calling `load_master_data()` from the `utils` file.
4.  `@st.cache_data` is used on these functions to ensure the API is only called once per session, maintaining high performance while ensuring data is present on every refresh.

### 2.3. Deployment Steps

1.  Log in to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"** and point it to the `agri-app-public` GitHub repository.
3.  Set the **Main file path** to `Trang_chu.py`.
4.  Click **"Advanced settings..."**.
5.  In the **"Secrets"** section, add the following secrets. This is how the frontend securely finds the backend API.

    ```toml
    # Points the frontend to the live Render API
    API_BASE_URL = "https://vietnam-agriculture-app-public-backend.onrender.com/docs"
    ```

6.  Click **"Deploy!"**. The application will build and become available at its public Streamlit URL.

---
**[Return to Main Project README](../README.md)**
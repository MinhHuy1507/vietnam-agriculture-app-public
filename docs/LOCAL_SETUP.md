# Installation and Local Setup Guide

This document provides detailed instructions on how to install and run the **Vietnam Agriculture Analytics** application on your local machine (Localhost).

## System Requirements

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** 3.9 or higher
- **Docker:** Docker Desktop (if using Option 1)
- **Git:** To clone the source code

---

## Option 1: Using Docker (Recommended) 🐳

The fastest and simplest way to run the entire system (including Database, Backend, and Frontend).

```powershell
# 1. Clone repository
git clone https://github.com/MinhHuy1507/vietnam-agriculture-app-public.git
cd vietnam-agriculture-app-public

# 2. Build and start services
docker-compose up -d --build

# 3. Check status
docker-compose ps
```

**Access the application:**
- 🎨 **Frontend (Streamlit):** http://localhost:8501
- ⚙️ **Backend API:** http://localhost:8000
- 📚 **API Documentation:** http://localhost:8000/docs

**Manage containers:**
```powershell
# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Option 2: Manual Setup (Development) 💻

Suitable for development and debugging. You need to run the Backend and Frontend in two separate terminals.

### Step 1: Install and Run Backend

Open the first terminal:

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv backend_venv

# 3. Activate environment
# Windows:
.\backend_venv\Scripts\activate
# macOS/Linux:
# source backend_venv/bin/activate

# 4. Run seed db file to seed data
python seed_db.py

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run API server (with hot-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend is ready at:** `http://localhost:8000`

### Step 2: Install and Run Frontend

Open the second terminal (keep the backend terminal running):

```powershell
# 1. Navigate to frontend directory (from project root)
cd frontend

# 2. Create virtual environment
python -m venv frontend_venv

# 3. Activate environment
# Windows:
.\frontend_venv\Scripts\activate
# macOS/Linux:
# source frontend_venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run Streamlit app
# Note: The main file name might be Trang_chu.py or home.py depending on the version
streamlit run Trang_chu.py
```

✅ **Frontend will automatically open at:** `http://localhost:8501`

---

## Troubleshooting

### 1. Database Connection Error
If the Backend reports a database connection error when running manually (Option 2), ensure you have PostgreSQL running locally or update the `.env` file (or environment variables) to point to the correct Database server.

If using Docker for the Database individually:
```powershell
docker-compose up -d app-db
```

### 2. Port already in use Error
If port 8000 or 8501 is already in use, stop the process using that port or change the port in the run command:
- Backend: `uvicorn main:app --port 8001`
- Frontend: `streamlit run Trang_chu.py --server.port 8502`

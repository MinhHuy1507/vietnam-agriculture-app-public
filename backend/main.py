"""
File: backend/main.py
Description:
    This is the main entry point for the Backend (FastAPI) application.
    This file is responsible for:
    1. Initializing the FastAPI application.
    2. Defining the 'startup' event to create database tables (from model.py).
    3. Defining all API endpoints (routes) that the Frontend will call:
        - GET /: Welcome page.
        - GET /db-test: Database connection verification.
        - GET /api/v1/statistics/provinces: Retrieve list of provinces.
        - GET /api/v1/statistics/agriculture-data: Retrieve agricultural data (with filtering).
        - GET /api/v1/statistics/climate-data: Retrieve climate data (with JOIN).
        - GET /api/v1/statistics/soil-data: Retrieve soil data (with JOIN).
        - POST /api/v1/predict: Accept 21 features and return predictions (currently using mock logic).
"""
from fastapi import FastAPI, Depends
from utils.connect_database import get_session, get_db_and_tables
from sqlmodel import Session, select

from typing import Annotated, List, Optional

from model import AgricultureData, ClimateData, Province, SoilData
from schemas import AgricultureDataRead, ClimateDataRead, ProvinceRead, SoilDataRead
from dependencies import AgricultureQuery, ClimateQuery, SoilQuery, PredictionInput, PredictionOutput

# --- 1. APPLICATION INITIALIZATION ---
app = FastAPI(
    title="Vietnam Agriculture API",
    description="API for querying agricultural, climate, and soil data, as well as yield prediction in Vietnam.",
    version="1.0.0"
)

# --- 2. STARTUP EVENT CONFIGURATION ---
@app.on_event("startup")
def start_up():
    """Invoke create_db_and_tables to initialize database and tables on startup event."""
    get_db_and_tables()

# --- 3. BASIC API ENDPOINTS ---
@app.get("/")
def init():
    return {"Welcome to Agriculture App"}

@app.get("/db-test")
def get_db_connection(session: Session = Depends(get_session)):
    """Endpoint to verify successful database connection."""
    try: 
        result= session.exec(select(1)).one()
        if result == 1:
                return {"status": "success", "message": "Database connection successful!", "result": result}
        else:
            return {"status": "fail", "message": "Connection successful but result is unexpected."}
        
    except Exception as e:
        return {"status": "error", "message": "Database connection failed.", "error_details": str(e)}
    
# --- 4. DATA RETRIEVAL API ENDPOINTS ---
@app.get("/api/v1/statistics/agriculture-data", response_model=list[AgricultureDataRead])
def get_agriculture_data(*, session: Annotated[Session, Depends(get_session)],
                         # Pagination parameters
                         skip: int = 0, # Skip first 'skip' records
                         limit: Optional[int] = 1000, # Retrieve maximum 'limit' records (default is 1000)
                         query_params: AgricultureQuery = Depends()):
    """
    API endpoint for retrieving agricultural data with filtering and pagination support.
    """
    query = select(AgricultureData)
    if query_params.year:
        query = query.where(AgricultureData.year == query_params.year)
    if query_params.commodity:
        query = query.where(AgricultureData.commodity == query_params.commodity)
    if query_params.season:
        query = query.where(AgricultureData.season == query_params.season)
    if query_params.region_name:
        query = query.where(AgricultureData.region_name == query_params.region_name)
    if query_params.region_level:
        query = query.where(AgricultureData.region_level == query_params.region_level)
    agriculture_data = session.exec(query.offset(skip).limit(limit)).all()
    return agriculture_data
    
@app.get("/api/v1/statistics/climate-data", response_model=list[ClimateDataRead])
def get_climate_data(*, session: Annotated[Session, Depends(get_session)],
                       # Pagination parameters
                       skip: int = 0,
                       limit: Optional[int] = 1000,
                       query_params: ClimateQuery = Depends()):
    """
    API endpoint for retrieving climate data.
    Automatically performs JOIN with Province table to retrieve 'province_name'.
    """
    query = select(ClimateData, Province).join(Province, ClimateData.province_id == Province.id)

    if query_params.year:
        query = query.where(ClimateData.year == query_params.year)
    
    if query_params.province_name:
        query = query.where(Province.province_name == query_params.province_name)
        
    query = query.offset(skip).limit(limit)
    
    # results_from_db is a list of tuples: [(climate1, province1), (climate2, province2), ...]
    results_from_db = session.exec(query).all()
    
    response = []
    for climate, province in results_from_db:
        data = climate.model_dump() 
        data['province_name'] = province.province_name 
        response.append(data)
    
    return response

@app.get("/api/v1/statistics/soil-data", response_model=List[SoilDataRead])
def get_soil_data(*, session: Annotated[Session, Depends(get_session)],
                  # Pagination parameters
                  skip: int = 0,
                  limit: Optional[int] = 1000,
                  query_params: SoilQuery = Depends()):
    """
    API endpoint for retrieving detailed soil data for each province.
    Automatically performs JOIN with Province table to retrieve 'province_name'.
    """
    query = select(SoilData, Province).join(Province, SoilData.province_id == Province.id)

    if query_params.province_name:
        query = query.where(Province.province_name == query_params.province_name)
        
    query = query.offset(skip).limit(limit)

    # results_from_db is a list of tuples: [(soil1, province1), (soil2, province2), ...]
    results_from_db = session.exec(query).all()
    
    response = []
    for soil, province in results_from_db:
        data = soil.model_dump()
        data['province_name'] = province.province_name 
        response.append(data)
    
    return response

@app.get("/api/v1/statistics/provinces", response_model=List[ProvinceRead])
def get_provinces(*, session: Annotated[Session, Depends(get_session)],
                  # Pagination parameters
                  skip: int = 0,
                  limit: Optional[int] = 100):
    """
    API endpoint for retrieving the list of all provinces/cities.
    """
    provinces = session.exec(select(Province).offset(skip).limit(limit)).all()
    return provinces

# --- 5. PREDICTION API ENDPOINT (POST) ---
@app.post("/api/v1/predict", response_model=PredictionOutput)
def post_prediction(
    *, 
    session: Annotated[Session, Depends(get_session)],
    input_data: PredictionInput
):
    """
    Prediction endpoint (CURRENTLY USING MOCK LOGIC).
    Accepts 21 input features and returns predicted production and area.
    
    TODO: Replace the "MOCK LOGIC" section with actual ML model invocation
          (e.g., model.predict(...)) when the model is ready.
    """
    predicted_area = 100 + (input_data.avg_temperature * 5)
    
    if input_data.commodity == "rice":
        predicted_production = predicted_area * (80 + (input_data.precipitation / 10))
    else:
        predicted_production = predicted_area * (40 + (input_data.precipitation / 10))
        
    predicted_yield = (predicted_production / predicted_area) * 10
    
    
    return PredictionOutput(
        predicted_production=predicted_production,
        predicted_area=predicted_area,
        predicted_yield=predicted_yield
    )
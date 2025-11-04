"""
File: backend/main.py
Description:
    Đây là file chạy chính (entrypoint) cho ứng dụng Backend (FastAPI).
    File này chịu trách nhiệm:
    1. Khởi tạo ứng dụng FastAPI.
    2. Định nghĩa sự kiện 'startup' để tạo bảng CSDL (từ model.py).
    3. Định nghĩa tất cả các API endpoint (đường dẫn) mà Frontend sẽ gọi:
        - GET /: Trang chào mừng.
        - GET /db-test: Kiểm tra kết nối CSDL.
        - GET /api/v1/statistics/provinces: Lấy danh sách tỉnh.
        - GET /api/v1/statistics/agriculture-data: Lấy dữ liệu nông nghiệp (có lọc).
        - GET /api/v1/statistics/climate-data: Lấy dữ liệu khí hậu (đã JOIN).
        - GET /api/v1/statistics/soil-data: Lấy dữ liệu thổ nhưỡng (đã JOIN).
        - POST /api/v1/predict: Nhận 21 features và trả về dự đoán (hiện tại đang dùng logic tạm thời).
"""
from fastapi import FastAPI, Depends
from utils.connect_database import get_session, get_db_and_tables
from sqlmodel import Session, select

from typing import Annotated, List, Optional

from model import AgricultureData, ClimateData, Province, SoilData
from schemas import AgricultureDataRead, ClimateDataRead, ProvinceRead, SoilDataRead
from dependencies import AgricultureQuery, ClimateQuery, SoilQuery, PredictionInput, PredictionOutput

# --- 1. KHỞI TẠO ỨNG DỤNG ---
app = FastAPI(
    title="Vietnam Agriculture API",
    description="API để truy vấn dữ liệu nông nghiệp, khí hậu, thổ nhưỡng và dự báo sản lượng tại Việt Nam.",
    version="1.0.0"
)

# --- 2. SỰ KIỆN KHỞI ĐỘNG (STARTUP EVENT) ---
@app.on_event("startup")
def start_up():
    """Gọi create_db_and_tables để tạo database và tables với sự kiện startup."""
    get_db_and_tables()

# --- 3. API ENDPOINTS CƠ BẢN ---
@app.get("/")
def init():
    return {"Welcome to Agriculture App"}

@app.get("/db-test")
def get_db_connection(session: Session = Depends(get_session)):
    """Endpoint để kiểm tra kết nối CSDL có thành công không."""
    try: 
        result= session.exec(select(1)).one()
        if result == 1:
                return {"status": "success", "message": "Kết nối CSDL thành công!", "result": result}
        else:
            return {"status": "fail", "message": "Kết nối thành công nhưng kết quả không như mong đợi."}
        
    except Exception as e:
        return {"status": "error", "message": "Kết nối CSDL thất bại.", "error_details": str(e)}
    
# --- 4. API ENDPOINTS (GET DATA) ---
@app.get("/api/v1/statistics/agriculture-data", response_model=list[AgricultureDataRead])
def get_agriculture_data(*, session: Annotated[Session, Depends(get_session)],
                         # Tham số phân trang (Pagination)
                         skip: int = 0, # Bỏ qua 'skip' record đầu tiên
                         limit: Optional[int] = 1000, # Lấy tối đa 'limit' record (mặc định là 1000)
                         query_params: AgricultureQuery = Depends()):
    """
    API lấy dữ liệu nông nghiệp, hỗ trợ lọc và phân trang.
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
                       # Tham số phân trang (Pagination)
                       skip: int = 0,
                       limit: Optional[int] = 1000,
                       query_params: ClimateQuery = Depends()):
    """
    API lấy dữ liệu khí hậu.
    Tự động JOIN với bảng Province để lấy 'province_name'.
    """
    query = select(ClimateData, Province).join(Province, ClimateData.province_id == Province.id)

    if query_params.year:
        query = query.where(ClimateData.year == query_params.year)
    
    if query_params.province_name:
        query = query.where(Province.province_name == query_params.province_name)
        
    query = query.offset(skip).limit(limit)
    
    # results_from_db là một danh sách các cặp: [(climate1, province1), (climate2, province2), ...]
    results_from_db = session.exec(query).all()
    
    response = []
    for climate, province in results_from_db:
        data = climate.model_dump() 
        data['province_name'] = province.province_name 
        response.append(data)
    
    return response

@app.get("/api/v1/statistics/soil-data", response_model=List[SoilDataRead])
def get_soil_data(*, session: Annotated[Session, Depends(get_session)],
                  # Tham số phân trang (Pagination)
                  skip: int = 0,
                  limit: Optional[int] = 1000,
                  query_params: SoilQuery = Depends()):
    """
    API lấy dữ liệu thổ nhưỡng (soil) chi tiết cho từng tỉnh.
    Tự động JOIN với bảng Province để lấy 'province_name'.
    """
    query = select(SoilData, Province).join(Province, SoilData.province_id == Province.id)

    if query_params.province_name:
        query = query.where(Province.province_name == query_params.province_name)
        
    query = query.offset(skip).limit(limit)

    # results_from_db là một danh sách các cặp: [(soil1, province1), (soil2, province2), ...]
    results_from_db = session.exec(query).all()
    
    response = []
    for soil, province in results_from_db:
        data = soil.model_dump()
        data['province_name'] = province.province_name 
        response.append(data)
    
    return response

@app.get("/api/v1/statistics/provinces", response_model=List[ProvinceRead])
def get_provinces(*, session: Annotated[Session, Depends(get_session)],
                  # Tham số phân trang (Pagination)
                  skip: int = 0,
                  limit: Optional[int] = 100):
    """
    API lấy danh sách tất cả các tỉnh/thành.
    """
    provinces = session.exec(select(Province).offset(skip).limit(limit)).all()
    return provinces

# --- 5. API ENDPOINT (POST PREDICT) ---
@app.post("/api/v1/predict", response_model=PredictionOutput)
def post_prediction(
    *, 
    session: Annotated[Session, Depends(get_session)],
    input_data: PredictionInput
):
    """
    Endpoint dự đoán (HIỆN TẠI ĐANG DÙNG LOGIC "GIẢ" - MOCK).
    Nhận 21 yếu tố đầu vào và trả về Sản lượng & Diện tích dự đoán.
    
    TODO: Thay thế khối "LOGIC GIẢ" bằng code gọi mô hình ML thật
          (ví dụ: model.predict(...)) khi mô hình đã sẵn sàng.
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
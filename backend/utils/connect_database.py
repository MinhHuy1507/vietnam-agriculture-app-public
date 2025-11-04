"""
File: backend/utils/connect_database.py
Description:
    File tiện ích (utility) này chịu trách nhiệm thiết lập
    kết nối đến Cơ sở dữ liệu PostgreSQL.
    
    Nó thực hiện các nhiệm vụ:
    1. Đọc các biến môi trường (DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT)
       để tạo chuỗi kết nối (URL) một cách linh hoạt.
    2. Cung cấp giá trị "mặc định" (default) để có thể chạy script
       ở local (ví dụ: chạy seed_db.py) mà không cần Docker.
    3. Tạo ra một 'engine' (bộ máy) SQLAlchemy duy nhất cho toàn bộ ứng dụng.
    4. Cung cấp hàm 'get_session' (Dependency Injection) để FastAPI
       có thể "mượn" một session kết nối cho mỗi API request.
"""
import os
from sqlmodel import create_engine, Session, SQLModel

# --- ĐỒNG BỘ HÓA CÁC GIÁ TRỊ MẶC ĐỊNH ---
DB_USER_DEFAULT = "vietnamagriculture"
DB_PASS_DEFAULT = "vietnamagriculture"
DB_NAME_DEFAULT = "vietnam_agriculture" 

# KHI CHẠY LOCAL: Host là 'localhost'
DB_HOST_DEFAULT = "localhost"
DB_PORT_DEFAULT = "5433" 

# --- ĐỌC BIẾN MÔI TRƯỜNG ---
# Khi chạy trong Docker, nó sẽ lấy các giá trị "thật"
# Khi chạy Local, nó sẽ lấy các giá trị "mặc định" ở trên
DB_USER = os.environ.get("DB_USER", DB_USER_DEFAULT)
DB_PASS = os.environ.get("DB_PASS", DB_PASS_DEFAULT)
DB_HOST = os.environ.get("DB_HOST", DB_HOST_DEFAULT)
DB_NAME = os.environ.get("DB_NAME", DB_NAME_DEFAULT)
DB_PORT = os.environ.get("DB_PORT", DB_PORT_DEFAULT)

# Tạo chuỗi kết nối (URL) động
URL_DB = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Tạo engine từ URL động
engine = create_engine(URL_DB, echo=True)

def get_session():
    """
    Hàm Dependency Injection (DI) cho FastAPI.
    
    Khi một endpoint yêu cầu một 'Session', FastAPI sẽ gọi hàm này.
    'yield session' sẽ "tiêm" session vào endpoint.
    Sau khi endpoint chạy xong, khối 'with' sẽ tự động
    đóng session lại, đảm bảo không bị rò rỉ kết nối.
    """
    with Session(engine) as session:
        yield session

def get_db_and_tables():
    """
    Hàm này được gọi khi server khởi động (trong main.py).
    Nó ra lệnh cho SQLModel tạo tất cả các bảng (đã định nghĩa trong model.py)
    nếu chúng chưa tồn tại.
    """
    SQLModel.metadata.create_all(engine)

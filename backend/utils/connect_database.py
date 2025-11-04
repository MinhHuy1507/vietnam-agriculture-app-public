"""
File: backend/utils/connect_database.py
Description:
    This utility file is responsible for establishing
    connection to the PostgreSQL database.
    
    It performs the following tasks:
    1. Reads environment variables (DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT)
       to create a flexible connection URL.
    2. Provides "default" values to enable running scripts
       locally (e.g., running seed_db.py) without Docker.
    3. Creates a single SQLAlchemy 'engine' for the entire application.
    4. Provides 'get_session' function (Dependency Injection) so FastAPI
       can "borrow" a session connection for each API request.
"""
import os
from sqlmodel import create_engine, Session, SQLModel

# --- SYNCHRONIZE DEFAULT VALUES ---
DB_USER_DEFAULT = "vietnamagriculture"
DB_PASS_DEFAULT = "vietnamagriculture"
DB_NAME_DEFAULT = "vietnam_agriculture" 

# WHEN RUNNING LOCALLY: Host is 'localhost'
DB_HOST_DEFAULT = "localhost"
DB_PORT_DEFAULT = "5433" 

# --- READ ENVIRONMENT VARIABLES ---
# When running in Docker, it will use the "real" values
# When running locally, it will use the "default" values above
DB_USER = os.environ.get("DB_USER", DB_USER_DEFAULT)
DB_PASS = os.environ.get("DB_PASS", DB_PASS_DEFAULT)
DB_HOST = os.environ.get("DB_HOST", DB_HOST_DEFAULT)
DB_NAME = os.environ.get("DB_NAME", DB_NAME_DEFAULT)
DB_PORT = os.environ.get("DB_PORT", DB_PORT_DEFAULT)

# Create dynamic connection URL
URL_DB = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine from dynamic URL
engine = create_engine(URL_DB, echo=True)

def get_session():
    """
    Dependency Injection (DI) function for FastAPI.
    
    When an endpoint requires a 'Session', FastAPI will call this function.
    'yield session' will "inject" the session into the endpoint.
    After the endpoint completes execution, the 'with' block will automatically
    close the session, ensuring no connection leaks.
    """
    with Session(engine) as session:
        yield session

def get_db_and_tables():
    """
    This function is called when the server starts (in main.py).
    It instructs SQLModel to create all tables (defined in model.py)
    if they don't already exist.
    """
    SQLModel.metadata.create_all(engine)

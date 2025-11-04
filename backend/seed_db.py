"""
File: backend/seed_db.py
Description:
    This is a standalone script used to "seed" data from CSV files
    (in the /data directory) into the PostgreSQL database.
    
    This script is NOT part of the API, but rather a
    utility tool that runs once to initialize the database environment.
    
    It is also used by 'docker-compose.yml' (via the 'db-seeder' service)
    to automatically load data on startup.

    Execution workflow:
    1. reset_database(): Drop and recreate all tables.
    2. insert_provinces_data(): Load province data (into 'province' table).
    3. get_province_id(): Create a lookup dictionary
       from {province_name -> id} for foreign key usage.
    4. insert_soil_data(): Load soil data, using the lookup map above to
       populate 'province_id'.
    5. insert_climate_data(): Load climate data, using the lookup map above to
       populate 'province_id'.
    6. insert_agriculture_data(): Load agriculture data, using the lookup map
       above to populate 'province_id' (for 'province' level rows).
"""
import pandas as pd
from sqlmodel import Session, SQLModel
from utils.connect_database import engine
from model import Province, ClimateData, AgricultureData
import os

# Define absolute path to the 'data' directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def reset_database():
    """
    Drop all database tables and recreate them
    based on 'model.py'. Ensures a clean start.
    """
    try:
        print("Resetting database")

        SQLModel.metadata.drop_all(engine) 
        SQLModel.metadata.create_all(engine)
        
        print("Reset database successfully")
    except Exception as e:
        print(f"Error resetting database: {e}")
        raise e
    
def insert_provinces_data(path: str):
    """
    Load data from 'province.csv' into the 'province' table.
    This is the "parent" table, must be loaded first.
    """
    try:
        print("Inserting provinces data")
        df_province = pd.read_csv(path)
        df_province.to_sql(
            name="province",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted provinces data successfully")
    except Exception as e:
        print(f"Error inserting provinces: {e}")

def get_province_id():
    """
    Read the 'province' table (after loading) to create a 
    lookup dictionary (map) {province_name -> id}.
    Example: {'An Giang': 1, 'Ba Ria - Vung Tau': 2, ...}
    
    Returns:
        dict: A dictionary mapping province names to IDs.
    """
    with Session(engine) as session:
        df_province_from_db = pd.read_sql("SELECT id, province_name FROM province", session.connection())
        province_map = pd.Series(df_province_from_db.id.values, 
                                 index=df_province_from_db.province_name).to_dict()
    return province_map


def insert_climate_data(path: str):
    """
    Load data from 'climate.csv' into the 'climate_data' table.
    Uses 'province_map' to populate the 'province_id' foreign key.
    """
    try:
        print("Inserting climate data")
        df_climate = pd.read_csv(path)
        province_map = get_province_id()
        
        df_climate['province_id'] = df_climate['province_name'].map(province_map)
        df_climate = df_climate.drop(columns=['province_name'])
        
        df_climate.to_sql(
            name="climate_data",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted climate data successfully")
    except Exception as e:
        print(f"Error inserting climate data: {e}")

def insert_soil_data(path: str):
    """
    Load data from 'soil.csv' into the 'soil_data' table.
    Uses 'province_map' to populate the 'province_id' foreign key.
    """
    try:
        print("Inserting soil data")
        df_soil = pd.read_csv(path)
        province_map = get_province_id()

        df_soil['province_id'] = df_soil['province_name'].map(province_map)
        df_soil = df_soil.drop(columns=['province_name'])

        df_soil.to_sql(
            name="soil_data",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted soil data successfully")
    except Exception as e:
        print(f"Error inserting soil data: {e}")

def insert_agriculture_data(path: str):
    """
    Load data from 'agriculture.csv' into the 'agriculture_data' table.
    Uses 'province_map' to populate the 'province_id' foreign key
    for rows where 'region_level' is 'province'.
    """
    try:
        print("Inserting agriculture data")
        df_agriculture = pd.read_csv(path)
        province_map = get_province_id()
        
        df_agriculture['province_id'] = df_agriculture['region_name'].map(province_map)
        level_map = {
            1: "province",
            2: "region",
            3: "country"
        }
        df_agriculture['region_level'] = df_agriculture['region_level'].map(level_map)

        df_agriculture.to_sql(
            name="agriculture_data",
            con=engine,
            if_exists="append",
            index=False
        )
        print("Inserted agriculture data successfully")
    except Exception as e:
        print(f"Error inserting agriculture data: {e}")

# MAIN
if __name__ == "__main__":
    """
    This is the main function, only runs when this script
    is called directly (e.g., 'python seed_db.py').
    """
    reset_database()
    insert_provinces_data(os.path.join(DATA_DIR, "province.csv"))
    insert_climate_data(os.path.join(DATA_DIR, "climate.csv"))
    insert_agriculture_data(os.path.join(DATA_DIR, "agriculture.csv"))
    insert_soil_data(os.path.join(DATA_DIR, "soil.csv"))
"""
File: frontend/utils/load_data.py
Description:
    This is the CENTRAL utility file responsible for
    loading all data for the Streamlit application.
    
    Subpages (in the /pages directory) will 'import' functions from this file
    instead of defining API call logic themselves.
"""

import streamlit as st
import pandas as pd
import requests
import os

# --- 1. DEFINE API BASE URL ---
# Read API URL from environment variable, use localhost if not available
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

# --- 2. API CALL FUNCTION (CHILD FUNCTION) ---
@st.cache_data(ttl=600)
def load_all_data_from_api(endpoint: str, params: dict = {}):
    """
    Generic API call function that automatically handles pagination to retrieve ALL data.
    """
    all_data = []
    page_size = 1000  
    skip = 0
    current_params = params.copy()
    current_params.pop('limit', None)
    current_params.pop('skip', None)
    current_params['limit'] = page_size
    current_params['skip'] = skip

    while True:
        try:
            full_url = f"{API_BASE_URL}/{endpoint}"
            response = requests.get(full_url, params=current_params)
            
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break 
                all_data.extend(data)
                skip += page_size
                current_params['skip'] = skip
            else:
                st.error(f"Error calling API {endpoint}: {response.status_code}")
                return pd.DataFrame() 
        except Exception as e:
            st.error(f"API connection error: {e}")
            return pd.DataFrame()
    
    return pd.DataFrame(all_data)

# --- 3. MASTER DATA LOADING FUNCTION (PARENT FUNCTION) ---
@st.cache_data(ttl=600)
def load_master_data():
    """
    Load all primary data sources from the API once.
    This function will be called by subpages.
    """
    with st.spinner("Loading master data..."):
        df_agri = load_all_data_from_api("statistics/agriculture-data")
        df_provinces = load_all_data_from_api("statistics/provinces")
        df_climate = load_all_data_from_api("statistics/climate-data")
        df_soil = load_all_data_from_api("statistics/soil-data")
        
        # Get df_regions from df_agri
        df_regions = df_agri[df_agri['region_level'] == 'region']

        # Process data types (critical for filtering)
        if 'year' in df_agri.columns:
            df_agri['year'] = pd.to_numeric(df_agri['year'], errors='coerce')
        if 'year' in df_climate.columns:
            df_climate['year'] = pd.to_numeric(df_climate['year'], errors='coerce')
                
        return df_agri, df_provinces, df_regions, df_climate, df_soil
import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

st.title("Sunbalance - UV & Vitamin D Tracker")

# User Settings
st.sidebar.header("User Settings")
latitude = st.sidebar.number_input("Latitude", value=19.4326)
longitude = st.sidebar.number_input("Longitude", value=-99.1332)

# Get UV Data
if st.button("Get UV Index"):
    try:
        # 使用 OpenUV API
        api_key = st.secrets["OPENUV_API_KEY"]
        response = requests.get(
            "https://api.openuv.io/api/v1/uv",
            params={"lat": latitude, "lng": longitude},
            headers={"x-access-token": api_key}
        )
        data = response.json()
        
        if response.status_code == 200:
            # UV Index Display
            uv = data["result"]["uv"]
            uv_max = data["result"]["uv_max"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current UV Index", f"{uv:.1f}")
            with col2:
                st.metric("Max UV Index", f"{uv_max:.1f}")
            
            # UV Index Gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = uv,
                domain = {"x": [0, 1], "y": [0, 1]},
                title = {"text": "UV Index"},
                gauge = {
                    "axis": {"range": [None, 12]},
                    "steps": [
                        {"range": [0, 3], "color": "lightgreen"},
                        {"range": [3, 6], "color": "yellow"},
                        {"range": [6, 8], "color": "orange"},
                        {"range": [8, 12], "color": "red"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": uv
                    }
                }
            ))
            st.plotly_chart(fig)
            
            # Safe Exposure Time
            st.subheader("Safe Exposure Time")
            # Calculate safe exposure time based on UV index
            safe_exposure_times = {
                "1": int(200/uv) if uv > 0 else 0,  # Very fair skin
                "2": int(250/uv) if uv > 0 else 0,  # Fair skin
                "3": int(300/uv) if uv > 0 else 0,  # Medium skin
                "4": int(400/uv) if uv > 0 else 0,  # Olive skin
                "5": int(500/uv) if uv > 0 else 0,  # Brown skin
                "6": int(600/uv) if uv > 0 else 0,  # Dark skin
            }
            
            for skin_type, time in safe_exposure_times.items():
                if time:
                    st.info(f"Skin Type {skin_type}: {time} minutes")
                    
        else:
            st.error(f"Failed to fetch data: {data.get("error", "Unknown error")}")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add information about skin types
with st.expander("Skin Type Information"):
    st.markdown("""
    - Type 1: Very fair skin, always burns, never tans
    - Type 2: Fair skin, burns easily, tans minimally
    - Type 3: Medium skin, burns moderately, tans gradually
    - Type 4: Olive skin, burns minimally, tans well
    - Type 5: Brown skin, rarely burns, tans deeply
    - Type 6: Dark skin, never burns, tans deeply
    """)

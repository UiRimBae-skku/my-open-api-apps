import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

@st.cache_data(ttl=600)
def get_coastal_weather(lat, lon):
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m",
            "hourly": "temperature_2m",
            "forecast_days": 2,
            "timezone": "auto",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    current = data["current"]
    hourly = data["hourly"]

    df = pd.DataFrame({
        "Time": pd.to_datetime(hourly["time"]),
        "Temperature (°C)": hourly["temperature_2m"],
    }).set_index("Time")

    return current, df

st.set_page_config(page_title="Deep Blue - Marine & Coastal Weather", page_icon="🌊", layout="centered")

st.title("🌊 Deep Blue: Coastal Weather Explorer")
st.caption("Arts and Advanced Big Data | Open API Service")

st.subheader("1. 지도에서 원하는 바다나 해안을 클릭하세요")
ocean_map = folium.Map(location=[35.5, 128.0], zoom_start=6)
map_output = st_folium(ocean_map, height=380, width=700)

clicked = (map_output or {}).get("last_clicked")
if not clicked:
    st.info("지도 위의 지점을 클릭하면 해당 위치의 실시간 해안 날씨 정보를 불러옵니다.")
    st.stop()

lat, lon = round(clicked["lat"], 3), round(clicked["lng"], 3)
st.subheader(f"2. 선택한 좌표: {lat}, {lon}")

try:
    current, df = get_coastal_weather(lat, lon)
except requests.RequestException:
    st.error("날씨 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("현재 기온", f"{current['temperature_2m']:.1f} °C")
col2.metric("풍속", f"{current['wind_speed_10m']:.1f} km/h")

st.subheader("3. 48시간 기온 변화 예보")
st.line_chart(df)
st.caption("Data source: Open-Meteo.com")

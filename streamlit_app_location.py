import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import numpy as np
import json
import base64

# 데이터 로딩을 위한 캐시 함수
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('location_snow_box.xlsx')
        df = df.dropna(subset='위도')
        return df
    except FileNotFoundError:
        st.error("데이터 파일이 없습니다.")
        return pd.DataFrame()

@st.cache_data
def load_geojson():
    try:
        with open("dohwa1.json", encoding='utf-8') as file:
            geo = json.loads(file.read())
        return geo
    except FileNotFoundError:
        st.error("GeoJSON 파일이 없습니다.")
        return {}

@st.cache_data
def load_logo():
    try:
        with open("image1.png", "rb") as f:
            logo_data = f.read()
        return base64.b64encode(logo_data).decode('utf-8')
    except FileNotFoundError:
        st.error("로고 파일이 없습니다.")
        return ""

# 맵 생성 함수
def create_map(df, geo, logo_img):
    map1 = folium.Map(location=[37.460898143, 126.673829865], zoom_start=15)
    
    # GeoJSON 추가
    if geo:
        folium.GeoJson(geo).add_to(map1)
    
    # 마커 추가
    for index, row in df.iterrows():
        folium.Marker(
            location=[row['위도'], row['경도']],
            popup=row['도로명주소'],
            tooltip=row['관리번호']
        ).add_to(map1)
    
    return map1

# 데이터 로딩
df = load_data()
geo = load_geojson()
logo_img = load_logo()

# 맵 생성 및 표시
if not df.empty and geo:
    map1 = create_map(df, geo, logo_img)
    st_folium(map1, width=700, height=500)
else:
    st.error("맵을 생성할 수 없습니다. 데이터를 확인하세요.")

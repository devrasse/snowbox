import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import numpy as np
import json
import base64
from streamlit.components.v1 import html

# 로고 파일 로드 함수
@st.cache_data
def load_logo():
    with open("image1.png", "rb") as f:
        logo_data = f.read()
    return base64.b64encode(logo_data).decode('utf-8')

# 페이지 설정
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# 지도 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_excel('location_snow_box.xlsx')
    df = df.dropna(subset='위도')
    return df

@st.cache_data
def load_geojson():
    with open("./dohwa1.json", encoding='utf-8') as file:
        geo = json.loads(file.read())
    return geo

# 지도 생성 함수
def create_map(df, geo, logo_img):
    map1 = folium.Map(location=[37.460898143, 126.673829865], zoom_start=15, min_zoom=10, max_zoom=18)

    # 각 제설함 위치에 마커 추가
    for index, row in df.iterrows():
        folium.Marker(
            [row['위도'], row['경도']],
            popup=row['도로명주소'],
            tooltip=row['관리번호'],
            icon=folium.Icon(color="blue")
        ).add_to(map1)

    # 로고 추가
    folium.FloatImage(
        'data:image/png;base64,{}'.format(logo_img),
        bottom=5, left=5, height=80, opacity=0.6
    ).add_to(map1)

    return map1

# 데이터 로드
df = load_data()
geo = load_geojson()
logo_img = load_logo()

# 사이드바 필터 설정
department = np.append(['전체'], df['관리부서'].unique())
selected_department = st.sidebar.selectbox('부서명', department)
if selected_department != '전체':
    selected_df = df[df['관리부서'] == selected_department]
else:
    selected_df = df

# 맵 생성
map1 = create_map(selected_df, geo, logo_img)

# Streamlit에서 folium 맵과 사용자 위치를 JS로 추적하여 표시
st_folium(map1, width=700, height=500, returned_objects=["last_clicked"], key="folium_map")

# 사용자 위치를 감지하는 JavaScript 삽입
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>User Location</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <script>
        navigator.geolocation.getCurrentPosition(
            (position) => {{
                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;
                var accuracy = position.coords.accuracy;

                // 사용자 위치 마커 생성 및 지도에 추가
                var userMarker = L.marker([latitude, longitude]).addTo(window.folium_map_object)
                    .bindPopup("현재 위치: 정확도 " + accuracy + "미터").openPopup();

                // 반경 원 추가
                var accuracyCircle = L.circle([latitude, longitude], {{ radius: accuracy }}).addTo(window.folium_map_object);
            }},
            (error) => {{
                console.error("위치 정보를 가져올 수 없습니다.", error);
            }}
        );
    </script>
</body>
</html>
"""

# JavaScript와 HTML 삽입
html(html_code)

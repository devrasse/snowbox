import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import re
import requests
import warnings
import numpy as np
import folium
from folium.plugins import MarkerCluster, Search, FloatImage, TagFilterButton, feature_group_sub_group, SideBySideLayers
import json
from datetime import datetime
import base64
from streamlit_lottie import st_lottie
from streamlit.components.v1 import html


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# 페이지 설정
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# 데이터 로딩을 위한 캐시 함수
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

@st.cache_data
def load_logo():
    with open("image1.png", "rb") as f:
        logo_data = f.read()
    return base64.b64encode(logo_data).decode('utf-8')

def wrap_text(words, max_line_length=20):
    words = words.split()
    wrapped_text = ''
    line_length = 0
    for word in words:
        if line_length + len(word) > max_line_length:
            wrapped_text += '<br>'
            line_length = 0
        wrapped_text += word + ' '
        line_length += len(word) + 1
    return wrapped_text

def create_map(df, geo, logo_img):
    # 맵 생성
    map1 = folium.Map(location=[37.460898143, 126.673829865], zoom_start=15, min_zoom=10, max_zoom=18)
    
    # 레이어 설정
    layer_right = folium.TileLayer(
        tiles='http://api.vworld.kr/req/wmts/1.0.0./CCA5DC05-6EDE-3BE5-A2DE-582966148562/Satellite/{z}/{y}/{x}.jpeg',
        attr='VWorldBase', name='VWorldBase', overlay=True, control=False, min_zoom=10
    )
    layer_left = folium.TileLayer(
        tiles='http://api.vworld.kr/req/wmts/1.0.0./CCA5DC05-6EDE-3BE5-A2DE-582966148562/Base/{z}/{y}/{x}.png',
        attr='VWorldBase', name='VWorldBase', overlay=True, control=False, min_zoom=10
    )

    sbs = SideBySideLayers(layer_left=layer_left, layer_right=layer_right)
    layer_left.add_to(map1)
    layer_right.add_to(map1)
    sbs.add_to(map1)

    # 스타일 설정
    style_function = lambda x: {"fillOpacity": 0, "opacity": 0.5}
    tooltip_style = 'font-size: 13px; max-width: 500px;'

    # GeoJSON 추가
    geojson = folium.GeoJson(geo, style_function, control=False)
    geojson.add_to(map1)

    # 마커 추가
    for index, row in df.iterrows():
        address = wrap_text(row['도로명주소'])
        popup_html = f"""
        <table style="width:100%; border-collapse: collapse; border: 2px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
            <tr>
                <td style="border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 5px;"><b>관리번호</b></td>
                <td style="border-bottom: 1px solid #ddd; padding: 5px;">{row['관리번호']}</td>
            </tr>
            <tr>
                <td style="border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 5px;"><b>주&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;소</b></td>
                <td style="border-bottom: 1px solid #ddd; padding: 5px;">{address}</td>
            </tr>
            <tr>
                <td style="border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 5px;"><b>내용물</b></td>
                <td style="border-bottom: 1px solid #ddd; padding: 5px;">{row['내용물']}</td>
            </tr>
        </table>
        """

        tooltip_html = f"""
        <b>관리번호:</b> {row['관리번호']}<br>
        """
        
        custom_icon = folium.CustomIcon(icon_image='snowbox.png', icon_size=(50, 50))
        marker = folium.Marker(
            [row['위도'], row['경도']], 
            icon=custom_icon,
            popup=folium.Popup(popup_html, style=tooltip_style, max_width=300),
            tooltip=folium.Tooltip(tooltip_html, style=tooltip_style),
            tags=[row['관리부서']]
        )
        marker.add_to(map1)

    # 로고 추가
    FloatImage(
        'data:image/png;base64,{}'.format(logo_img),
        bottom=5, left=5, height=80, opacity=0.6
    ).add_to(map1)
    
    return map1

# 스타일 설정
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 0.5vh;
    }
    .stSpinner > div > div {
        border-color: #1A9F68 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 타이틀 표시
st.markdown('<div class="centered"><h1 style="text-align:center;">미추홀구 제설함 위치도</h1></div>', unsafe_allow_html=True)
st.title("   ")

# 데이터 로딩 상태를 표시할 컨테이너
loading_container = st.empty()

# 로티 파일 로드
lottie_loading = load_lottiefile("lottiefiles/loading.json")

with loading_container.container():
    # 로티 애니메이션 표시
    st_lottie(lottie_loading, height=300, key="loading")
    
    with st.spinner('데이터를 불러오는 중입니다...'):
        # 데이터 로드
        df = load_data()
        geo = load_geojson()
        logo_img = load_logo()

        # 사이드바 필터 설정
        department = np.append(['전체'], df['관리부서'].unique())
        selected_department = st.sidebar.selectbox('부서명', department)

        # 선택된 부서에 따라 데이터 필터링
        if selected_department != '전체':
            selected_df = df[df['관리부서'] == selected_department]
        else:
            selected_df = df  # 전체 데이터 사용
        
        # 맵 생성
        map1 = create_map(selected_df, geo, logo_img)

# 로딩 컨테이너 제거
loading_container.empty()

# 맵 표시
st_data = st_folium(
    map1,
    width=1000,
    height=500,
    returned_objects=["last_clicked"],
    key="folium_map"
)

# 위치 추적을 위한 HTML 코드 수정
html_code = """
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
            (position) => {
                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;
                var accuracy = position.coords.accuracy;

                // Streamlit의 Folium에 사용자 위치 정보 전달
                window.parent.postMessage(
                    JSON.stringify({
                        latitude: latitude,
                        longitude: longitude,
                        accuracy: accuracy
                    }),
                    "*"
                );
            },
            (error) => {
                console.error("위치 정보를 가져올 수 없습니다.", error);
            }
        );
    </script>
</body>
</html>
"""

# JavaScript로부터 위치 정보를 수신하여 Folium에 표시
st.components.v1.html(html_code)

# 위치 정보를 수신하고 지도에 반영
user_location = st_folium(map1, width=1000, height=500, returned_objects=["last_clicked"], key="folium_map")

if "latitude" in user_location and "longitude" in user_location:
    folium.Marker(
        [user_location["latitude"], user_location["longitude"]],
        popup="현재 위치",
        tooltip="현재 위치",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(map1)
    st_folium(map1, width=1000, height=500)
else:
    st.warning("위치 정보를 가져오는 중입니다.")

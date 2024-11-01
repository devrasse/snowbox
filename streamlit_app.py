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

# 동별 중심 좌표 데이터
dong_centers = {
    '숭의2동': [37.46091, 126.6476],
    '숭의4동': [37.46236, 126.6571],
    '용현2동': [37.45616, 126.6435],
    '용현3동': [37.45537, 126.6527],
    '용현5동': [37.44897, 126.639],
    '학익1동': [37.441, 126.655],
    '학익2동': [37.4415, 126.6741],
    '도화1동': [37.46217, 126.6692],
    '주안1동': [37.46202, 126.6806],
    '주안2동': [37.45456, 126.6713],
    '주안3동': [37.44845, 126.6716],
    '주안4동': [37.45444, 126.6871],
    '주안5동': [37.46922, 126.6805],
    '주안6동': [37.46102, 126.6908],
    '주안7동': [37.44726, 126.6778],
    '주안8동': [37.44765, 126.6853],
    '관교동': [37.44273, 126.694],
    '문학동': [37.43653, 126.6853],
    '숭의1.3동': [37.46683, 126.6469],
    '용현1.4동': [37.45177, 126.6589],
    '도화2.3동': [37.47351, 126.6623],
}

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

def create_map(df, geo, radius, selected_dong='전체'):
    # 맵 중심 좌표 설정
    if selected_dong != '전체' and selected_dong in dong_centers:
        center_location = dong_centers[selected_dong]
        zoom_start = 16  # 동 선택시 더 가깝게 확대
    else:
        center_location = [37.460898143, 126.673829865]  # 기본 중심점
        zoom_start = 15  # 기본 줌 레벨

    # 맵 생성
    map1 = folium.Map(location=center_location, zoom_start=zoom_start, min_zoom=10, max_zoom=17)
    
    basemaps_vworld = {
        'VWorldBase': folium.TileLayer(
            tiles='http://api.vworld.kr/req/wmts/1.0.0./CCA5DC05-6EDE-3BE5-A2DE-582966148562/Base/{z}/{y}/{x}.png',
            attr = 'VWorldBase', name='VWorldBase', overlay= True, control= False, min_zoom= 10)
    }
    
    basemaps_vworld['VWorldBase'].add_to(map1)

    # 스타일 설정
    style_function = lambda x: {"fillOpacity": 0, "opacity": 0.5}
    tooltip_style = 'font-size: 13px; max-width: 500px;'

    # GeoJSON 추가 - 하이라이트 기능 포함
    geojson = folium.GeoJson(
        geo,
        style_function=style_function,
        control=False,
        zoom_on_click=True,
        highlight_function=lambda feature: {
            "fillColor": (
                "green" if "e" in feature["properties"]["adm_nm"].lower() else "#ffff00"
            ),
            "fillOpacity": 0.3,
            "color": "#3388ff",
            "weight": 3
        }
    )
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

        # 반경 그리기 (반경이 0이 아닐 때만)
        if radius != 0:
            circle = folium.Circle(
                location=[row['위도'], row['경도']],
                radius=radius,
                color='blue',
                fill=True,
                popup=f'반경 {radius}m'
            )
            circle.add_to(map1)
    
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

        circle = [0,50,100,200]
        radius = st.sidebar.selectbox('반경', circle)

        # 선택된 부서에 따라 데이터 필터링
        if selected_department != '전체':
            selected_df = df[df['관리부서'] == selected_department]
        else:
            selected_df = df  # 전체 데이터 사용
        
        # 맵 생성
        map1 = create_map(selected_df, geo, radius, selected_department)

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
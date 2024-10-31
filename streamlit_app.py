import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import re
import requests
import warnings
import numpy as np
import folium
from folium.plugins import MarkerCluster, Search, FloatImage, TagFilterButton, feature_group_sub_group, SideBySideLayers, LocateControl
import json
from datetime import datetime
import base64
from streamlit_lottie import st_lottie

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


ef create_map(df, geo, logo_img):
    # 맵 생성
    map1 = folium.Map(location=[37.460898143, 126.673829865], zoom_start=15, min_zoom=10, max_zoom=18)
    
    # JavaScript 코드로 현재 위치 기능 구현
    location_js = """
        function locate() {
            if ('geolocation' in navigator) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        var lat = position.coords.latitude;
                        var lng = position.coords.longitude;
                        map.setView([lat, lng], 16);
                        L.marker([lat, lng], {
                            icon: L.divIcon({
                                className: 'current-location',
                                html: '<div style="background-color: #4A90E2; width: 12px; height: 12px; border-radius: 50%; border: 3px solid white;"></div>'
                            })
                        }).addTo(map);
                    },
                    function(error) {
                        alert('위치를 찾을 수 없습니다.');
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0
                    }
                );
            } else {
                alert('위치 서비스를 지원하지 않는 브라우저입니다.');
            }
        }
    """
    
    # CSS 스타일 추가
    css = """
    <style>
        .locate-button {
            background-color: white;
            width: 30px;
            height: 30px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 1px 5px rgba(0,0,0,0.65);
            cursor: pointer;
            margin: 10px;
            position: relative;
            z-index: 1000;
        }
        .locate-button:hover {
            background-color: #f4f4f4;
        }
        .current-location {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        .locate-control {
            position: absolute;
            top: 80px;
            left: 10px;
            z-index: 1000;
        }
    </style>
    """
    
    # 현재 위치 버튼 생성
    locate_control = folium.Element("""
        <div class='locate-control'>
            <div class='locate-button' onclick='locate()' title='현재 위치'>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="8"/>
                    <line x1="12" y1="2" x2="12" y2="4"/>
                    <line x1="12" y1="20" x2="12" y2="22"/>
                    <line x1="2" y1="12" x2="4" y2="12"/>
                    <line x1="20" y1="12" x2="22" y2="12"/>
                </svg>
            </div>
        </div>
    """)

    # 요소들을 지도에 추가
    map1.get_root().header.add_child(folium.Element(css))
    map1.get_root().script.add_child(folium.Element(location_js))
    map1.get_root().html.add_child(locate_control)
    
    basemaps_vworld = {
        'VWorldBase': folium.TileLayer(
            tiles='http://api.vworld.kr/req/wmts/1.0.0./CCA5DC05-6EDE-3BE5-A2DE-582966148562/Base/{z}/{y}/{x}.png',
            attr = 'VWorldBase', name='VWorldBase', overlay= True, control= False, min_zoom= 10)
    }
    
    basemaps_vworld['VWorldBase'].add_to(map1)

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
    .folium-map {
        margin: 0 auto;
        width: 100% !important;
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
_,col1,_ = st.columns([0.1,0.8,0.1])
with col1:
    st_data = st_folium(
        map1,
        width=1200,
        height=800,
        returned_objects=["last_clicked"],
        key="folium_map"
    )
#st_data = st_folium(map1, width=1000, height=500)
# # 맵 표시
# with st.container(border=True,height=740):
#       st_data = st_folium(
#             map1,
#             width="100%",
#             height=700,
#             returned_objects=["last_clicked"],
#             key="folium_map"
#       )
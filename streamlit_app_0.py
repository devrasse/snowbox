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

# 부서명 리스트
departments = [
    '숭의1.3동','숭의2동','숭의4동','용현1.4동','용현2동','용현3동','용현5동','학익1동','학익2동','도화1동','도화2.3동',
    '주안1동','주안2동','주안3동','주안4동','주안5동','주안6동','주안7동','주안8동','관교동','문학동'
]


image_path = 'snowbox.png'

with open("image1.png", "rb") as f:
      data = f.read()
logo_img = base64.b64encode(data).decode('utf-8')

df = pd.read_excel('location_snow_box.xlsx')

df = df.dropna(subset='위도')

unique_dongs = df['관리부서'].unique().tolist()

dongs = []
# 없는 시트는 기존 순서대로 추가
for department in departments:
      if department in unique_dongs:
            dongs.append(department)


# 스트림릿 페이지 제목
st.title("미추홀구 제설함 위치도")

# 기본 위치 (서울)로 지도 초기화
map1 = folium.Map(location=[37.460898143, 126.673829865], zoom_start=15, min_zoom = 10, max_zoom=18)

basemaps_vworld = {
      'VWorldBase': folium.TileLayer(
            tiles='http://api.vworld.kr/req/wmts/1.0.0./CCA5DC05-6EDE-3BE5-A2DE-582966148562/Base/{z}/{y}/{x}.png',
            attr = 'VWorldBase', name='VWorldBase', overlay= True, control= False, min_zoom= 10)
}

basemaps_vworld['VWorldBase'].add_to(map1)
# layer_right = folium.TileLayer(
#     tiles='http://api.vworld.kr/req/wmts/1.0.0./CCA5DC05-6EDE-3BE5-A2DE-582966148562/Satellite/{z}/{y}/{x}.jpeg',
#     attr = 'VWorldBase', name='VWorldBase', overlay= True, control= False, min_zoom= 10
# )
# layer_left = folium.TileLayer(
#     tiles='http://api.vworld.kr/req/wmts/1.0.0./CCA5DC05-6EDE-3BE5-A2DE-582966148562/Base/{z}/{y}/{x}.png',
#     attr = 'VWorldBase', name='VWorldBase', overlay= True, control= False, min_zoom= 10
# )

# sbs = SideBySideLayers(layer_left=layer_left, layer_right=layer_right)

# layer_left.add_to(map1)
# layer_right.add_to(map1)
# sbs.add_to(map1)


style_function = lambda x: {
    "fillOpacity" : 0,
    "opacity" : 0.5} 

# 동별 행정구역 경계 표시
with open("./dohwa1.json", encoding='utf-8') as file:
    geo = json.loads(file.read())
    file.close()

geojson = folium.GeoJson(geo, style_function, control= False)

tooltip_style = 'font-size: 13px; max-width: 500px;'  # 원하는 너비로 조정

for index, row in df.iterrows():
    관리번호 = row['관리번호']
    주소 = row['도로명주소']
    내용물 = row['내용물']
    
    address = wrap_text(주소)
    
    popup_html = f"""
    <table style="width:100%; border-collapse: collapse; border: 2px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
        <tr>
            <td style="border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 5px;"><b>관리번호</b></td>
            <td style="border-bottom: 1px solid #ddd; padding: 5px;">{관리번호}</td>
        </tr>
        <tr>
            <td style="border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 5px;"><b>주&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;소</b></td>
            <td style="border-bottom: 1px solid #ddd; padding: 5px;">{address}</td>
        </tr>
        <tr>
            <td style="border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 5px;"><b>설치일시</b></td>
            <td style="border-bottom: 1px solid #ddd; padding: 5px;">{내용물}</td>
        </tr>
    </table>
    """

    tooltip_html = f"""
    <b>관리번호:</b> {관리번호}<br>
    """
    
    custom_icon = folium.CustomIcon(icon_image=image_path, icon_size=(50, 50))
    marker = folium.Marker([row['위도'], row['경도']], icon = custom_icon, popup = folium.Popup(popup_html, style= tooltip_style,  max_width=300), tooltip = folium.Tooltip(tooltip_html, style= tooltip_style) ,tags=[row['관리부서']])
    marker.add_to(map1)

    geojson.add_to(map1)

    FloatImage('data:image/png;base64,{}'.format(logo_img),
            bottom=5, left=5, height= 80, opacity=0.6).add_to(map1)
    
# 폴리움 맵을 스트림릿에 표시
st_data = st_folium(map1, width=1000, height=500)
import json
import requests  # pip install requests
import streamlit as st  # pip install streamlit
from streamlit_lottie import st_lottie  # pip install streamlit-lottie
import pandas as pd
import time
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pearsonr


# GitHub: https://github.com/andfanilo/streamlit-lottie
# Lottie Files: https://lottiefiles.com/

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#st.title(':bar_chart: 2024년 미추홀구 예산')
#st.markdown('<style>div.block-containner{padding-top:1rem;}</style>', unsafe_allow_html=True)

# 화면 중앙에 위치하도록 스타일 설정
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 0.5vh;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 제목을 div 태그로 감싸서 스타일 적용
st.markdown('<div class="centered"><h1 style="text-align:center;">📊 2024년 미추홀구 예산</h1></div>', unsafe_allow_html=True)
st.title("   ")

lottie_loading = load_lottiefile("lottiefiles/loading.json")  # replace link to local lottie file
loading_state = st.empty()
#lottie_hello = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_M9p23l.json")
#lottie_loading = load_lottieurl("https://lottie.host/efece630-073b-49e3-8240-1a8a9c118346/KbRGnvFFOG.json")
# st_lottie(
#     lottie_loading,
#     speed=1,
#     reverse=False,
#     loop=True,
#     quality="low", # medium ; high
#     renderer="canvas", # svg, canvas
#     height=None,
#     width=None,
#     key=None,
# )
with loading_state.container():
    with st.spinner('데이터 읽어오는 중...'):
        st_lottie(lottie_loading)
        df = pd.read_excel('budget_2024.xlsx')
    st.success('로딩 완료!')
    
loading_state.empty()

budget = df.copy()
budget = budget.dropna(subset=['산출근거식'])
# #budget.drop(0, inplace=True)
selected_columns = ['회계연도', '예산구분', '세부사업명', '부서명', '예산액', '자체재원']
budget = budget[selected_columns]
budget['자체재원'] = budget['자체재원'].replace('경정', '', regex=True)
budget['회계연도'] = budget['회계연도'].fillna(0).replace(float('inf'), 0).astype(int)
budget['회계연도'] = budget['회계연도'].astype(str)
budget['자체재원'] = budget['자체재원'].fillna(0).apply(lambda x: int(x) if str(x).isdigit() and x != '' else 0)

budget = budget.groupby(['부서명']).sum()
budget = budget.reset_index()
budget['회계연도'] = "2024년"
budget = budget[['회계연도','부서명','예산액','자체재원']]

with st.expander("2024년 미추홀구 예산", expanded=False):
    st.dataframe(budget,use_container_width=True)


col1, col2 = st.columns(2)

budget['자체재원'] = (budget['자체재원']  / 1000).apply(np.floor)
budget['예산액'] = (budget['예산액']  / 1000).apply(np.floor)
budget = budget.sort_values(by='예산액',ascending=False)

# fig = px.bar(budget, x='부서명', y='예산액',
#               #color_discrete_map=color_discrete_map,
#               title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub> ', labels={'자체재원': '구비', '부서명': '부서명'},
#               template= 'simple_white')
# #fig.update_layout(yaxis_tickformat=',.0s')
# fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
# #fig.update_layout(title_x=0.5)
# fig.update_xaxes(tickangle=45)
with col1:
    fig = px.pie(budget, values='예산액', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황</b><br><sub>2024년 부서별 예산현황</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    budget_top10 = budget.nlargest(10,'예산액')
    budget_top10 = budget_top10.sort_values(by='예산액',ascending=False)

    fig = px.bar(budget_top10, x='부서명', y='예산액',
                #color_discrete_map=color_discrete_map,
                title='<b>미추홀구 예산 현황</b><br><sub>2024년 상위10개부서</sub> ', labels={'예산액': '예산액', '부서명': '부서명'},
                template= 'simple_white',text = budget_top10['예산액'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황</b><br><sub>2024년 상위10개부서</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2) 
budget = budget.sort_values(by='자체재원',ascending=False)
with col1:
    fig = px.pie(budget, values='자체재원', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 부서별 예산현황</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    budget_top10_self = budget.nlargest(10,'자체재원')
    budget_top10_self = budget_top10_self.sort_values(by='자체재원',ascending=False)

    fig = px.bar(budget_top10_self, x='부서명', y='자체재원',
                #color_discrete_map=color_discrete_map,
                title='<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 상위10개부서</sub> ', labels={'자체재원': '예산액(구비)', '부서명': '부서명'},
                template= 'simple_white',text = budget_top10_self['예산액'].apply(lambda x: f'{x:,.0f}'))
    #fig.update_layout(yaxis_tickformat=',.0s')

    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 상위10개부서</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)
    
st.markdown("---")
col1, col2 = st.columns(2) 

col1.write(
    """
    <div style="margin-right: 30px;">
    """,
    unsafe_allow_html=True
)

with col1:
    fig = px.treemap(budget, path=['부서명'], values='예산액',
        height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Set2) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': '2024년 미추홀구 예산 현황',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = dict(t=100, l=25, r=25, b=25))
    fig.update_traces(marker = dict(line=dict(width = 1, color = 'black')))
    fig.update_traces(texttemplate='%{label}: %{value:,.0f}백만원' , textposition='middle center',
                    textfont_color='black')
    fig.update_traces(#hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    fig.update_traces(hoverlabel=dict(font_size=16, font_family="Arial", font_color="white"))
    fig.update_layout(font=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)

col1.write("</div>", unsafe_allow_html=True)

with col2:
    fig = px.treemap(budget, path=['부서명'], values='자체재원',
        height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Set1) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': '2024년 미추홀구 예산 현황(구비)',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = dict(t=100, l=25, r=25, b=25))
    fig.update_traces(marker = dict(line=dict(width = 1, color = 'black')))
    fig.update_traces(texttemplate='%{label}: %{value:,.0f}백만원' , textposition='middle center', 
                    textfont_color='black') 
    fig.update_traces(#hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    fig.update_traces(hoverlabel=dict(font_size=16, font_family="Arial", font_color="white"))
    fig.update_layout(font=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)   

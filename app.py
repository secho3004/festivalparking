import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="축제 & 주차 대시보드", layout="wide")
st.title("📊 전국 문화축제 & 주차 인프라 분석 대시보드")
st.markdown("전국의 축제 현황과 주차 시설 데이터를 비교 분석하여 인프라 격차를 파악합니다.")

# 2. 데이터베이스 연결 및 에러 처리
DB_PATH = 'festival_parking.db'

def get_connection():
    if not os.path.exists(DB_PATH):
        st.error(f"⚠️ 데이터베이스 파일('{DB_PATH}')을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요!")
        st.stop()
    return sqlite3.connect(DB_PATH)

conn = get_connection()

# --- 시각화 함수 정의 ---

def plot_chart_1():
    st.subheader("1. 시도별 축제 수 vs 총 주차구획수")
    # SQL: 시도별 축제와 주차구획수 조회
    query = "SELECT 시도, 축제수, 총주차구획수 FROM region_summary"
    df = pd.read_sql(query, conn)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['시도'], y=df['축제수'], name='축제 수', yaxis='y1'))
    fig.add_trace(go.Bar(x=df['시도'], y=df['총주차구획수'], name='총 주차구획수', yaxis='y2'))
    
    fig.update_layout(
        yaxis=dict(title="축제 수 (개)"),
        yaxis2=dict(title="주차구획 수 (면)", overlaying='y', side='right'),
        barmode='group',
        legend=dict(x=1.1, y=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("**SQL:** `SELECT 시도, 축제수, 총주차구획수 FROM region_summary`  \n"
            "**인사이트:** 특정 지역(예: 강원, 제주)은 축제 수 대비 주차 구획수가 부족할 수 있습니다. "
            "막대의 높이 차이를 통해 인프라 확충이 필요한 지자체를 식별할 수 있습니다.")

def plot_chart_2():
    st.subheader("2. 월별 축제 개최 현황")
    # SQL: 월별 축제 수와 평균 기간 계산
    query = """
    SELECT 월, COUNT(*) as 축제수, AVG(기간_일수) as 평균기간 
    FROM festival 
    GROUP BY 월 ORDER BY 월
    """
    df = pd.read_sql(query, conn)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['월'], y=df['축제수'], name='축제 수'))
    fig.add_trace(go.Scatter(x=df['월'], y=df['평균기간'], name='평균 기간(일)', mode='lines+markers', yaxis='y2'))
    
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        yaxis=dict(title="축제 수"),
        yaxis2=dict(title="평균 기간(일)", overlaying='y', side='right')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("**SQL:** `SELECT 월, COUNT(*), AVG(기간_일수) FROM festival GROUP BY 월`  \n"
            "**인사이트:** 봄(4~5월)과 가을(9~10월)에 축제가 집중되는 계절적 패턴을 보입니다. "
            "축제 기간이 긴 월은 장기적인 교통 통제 대책이 추가로 필요함을 시사합니다.")

def plot_chart_3():
    st.subheader("3. 시도별 공영 vs 민영 주차장 비율")
    # SQL: 시도 및 구분별 주차장 수 집계
    query = "SELECT 시도, 주차장구분, COUNT(*) as 개수 FROM parking GROUP BY 시도, 주차장구분"
    df = pd.read_sql(query, conn)
    
    fig = px.bar(df, x="시도", y="개수", color="주차장구분", 
                 barmode="relative", text_auto=True,
                 title="지역별 주차장 운영 주체 비율 (100% Stacked)")
    
    # 100% 스택 막대 차트로 변환 (정규화)
    fig.update_layout(barnorm='percent')
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("**SQL:** `SELECT 시도, 주차장구분, COUNT(*) FROM parking GROUP BY 시도, 주차장구분`  \n"
            "**인사이트:** 대부분의 지역에서 공영 주차장 비중이 압도적으로 높습니다. "
            "민영 주차장 비율이 낮은 지역은 축제 시 민간 협력 주차 공간 확보가 어려울 수 있음을 나타냅니다.")

def plot_chart_4():
    st.subheader("4. 축제 수 대비 주차구획수 산점도")
    # SQL: 축제당 주차구획수 계산
    query = """
    SELECT 시도, 축제수, (CAST(총주차구획수 AS FLOAT) / 축제수) as 축제당_주차구획수 
    FROM region_summary
    """
    df = pd.read_sql(query, conn)
    
    fig = px.scatter(df, x="축제수", y="축제당_주차구획수", text="시도", 
                     size="축제수", color="시도",
                     labels={"축제당_주차구획수": "축제 1개당 평균 주차면수"})
    
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("**SQL:** `SELECT 시도, 축제수, (총주차구획수 / 축제수) FROM region_summary`  \n"
            "**인사이트:** 우측 하단에 위치한 지역은 축제는 많지만 축제당 주차 인프라는 매우 열악한 곳입니다. "
            "반면 좌상단 지역은 상대적으로 여유로운 주차 환경을 제공하고 있습니다.")

# --- 메인 실행 화면 ---
col1, col2 = st.columns(2)

with col1:
    plot_chart_1()
    st.divider()
    plot_chart_3()

with col2:
    plot_chart_2()
    st.divider()
    plot_chart_4()

# 연결 종료
conn.close()
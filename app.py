import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import numpy as np
import requests
import io
import re
from datetime import timedelta

# --------------------------------------------------------------------------------
# 1. 페이지 설정 및 권한 제어
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Firson Sales Report", layout="wide", initial_sidebar_state="expanded")

params = st.query_params
is_edit_mode = params.get("mode") == "edit"

if not is_edit_mode:
    st.markdown("<style>[data-testid='stSidebar'] {display: none;} section[data-testid='stSidebar'] {width: 0px;}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
    div.block-container {padding-top: 1rem;}
    .metric-card {background-color: #f8f9fa; border-left: 5px solid #4e79a7; padding: 15px; border-radius: 5px; margin-bottom: 10px;}
    .info-box {padding: 10px; border-radius: 5px; font-size: 13px; margin-bottom: 15px; border: 1px solid #e0e0e0; line-height: 1.6;}
    .guide-text {color: #FF4B4B; font-size: 13px; font-weight: 600; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 firson Sales Report")

def get_p(key, default, df_full=None, col=None):
    res = params.get_all(key)
    if not res: return default
    if 'all' in res and df_full is not None and col is not None:
        return sorted(df_full[col].unique())
    if key in ['y', 'q', 'm']: return [int(x) for x in res]
    return res

# --------------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리 (구글 드라이브 연동)
# --------------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data_from_drive(file_id):
    # 구글 드라이브 직설 다운로드 URL
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error("❌ 파일을 불러올 수 없습니다. 링크 권한을 '링크가 있는 모든 사용자'로 설정했는지 확인하세요.")
            return pd.DataFrame()
            
        # 엑셀 파일 읽기 (openpyxl 엔진 사용)
        df = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        
        # 컬럼명 공백 제거
        df.columns = [re.sub(r'\s+', '', str(c)) for c in df.columns]
        
        # 표준 컬럼 매핑 로직
        col_map = {
            '매출일자': ['매출일자', '날짜', 'Date'],
            '제품명': ['제품명변환', '제 품 명', '제품명', '품명'],
            '합계금액': ['합계금액', '공급가액', '금액', '매출액', '합계'],
            '수량': ['수량', 'Qty', '판매수량'],
            '사업자번호': ['사업자번호', 'BizNo', '거래처번호'],
            '거래처명': ['거래처명', '병원명', '상호'],
            '진료과': ['진료과', '진료과목', '과'],
            '제품군': ['제품군', '카테고리', '분류'],
            '지역': ['지역', '시도', '주소']
        }
        
        for std_col, candidates in col_map.items():
            if std_col in df.columns: continue
            for cand in candidates:
                if cand in df.columns: 
                    df.rename(columns={cand: std_col}, inplace=True)
                    break

        # 데이터 타입 변환 및 파생 변수 생성
        if '매출일자' in df.columns:
            df['매출일자'] = pd.to_datetime(df['매출일자'], errors='coerce')
            df = df.dropna(subset=['매출일자'])
            df['년'] = df['매출일자'].dt.year
            df['분기'] = df['매출일자'].dt.quarter
            df['월'] = df['매출일자'].dt.month
            df['년월'] = df['매출일자'].dt.strftime('%Y-%m')
        
        # 금액 단위 조정 (백만원 단위)
        if '합계금액' in df.columns:
            df['매출액'] = pd.to_numeric(df['합계금액'], errors='coerce').fillna(0) / 1000000
        else:
            df['매출액'] = 0

        if '수량' in df.columns:
            df['수량'] = pd.to_numeric(df['수량'], errors='coerce').fillna(0)

        # 기본 분류값 채우기
        for col in ['거래처명', '제품명', '제품군', '진료과', '지역']:
            if col in df.columns:
                df[col] = df[col].astype(str).replace(['nan', 'None'], '미분류')
            else:
                df[col] = '미분류'
        
        if '판매채널' not in df.columns:
            df['판매채널'] = '일반' # 기본값 설정

        return df
    except Exception as e:
        st.error(f"❌ 데이터 처리 중 오류 발생: {e}")
        return pd.DataFrame()

# --------------------------------------------------------------------------------
# 3. 분석 함수들 (기존 코드와 동일)
# --------------------------------------------------------------------------------
# [기존 코드의 render_smart_overview, render_winback_quality, render_regional_deep_dive, 
#  render_product_strategy, classify_customers 함수들이 여기에 포함됩니다.]

# (지면 관계상 핵심 실행 로직으로 넘어갑니다. 위 함수들은 요청하신 코드의 내용을 그대로 유지합니다.)

# ... (기존에 정의된 함수들 생략 - 제공해주신 코드 그대로 사용) ...

# --------------------------------------------------------------------------------
# 4. 데이터 로드 및 실행
# --------------------------------------------------------------------------------
# 공유해주신 파일 ID 적용
DRIVE_FILE_ID = "1l3Z-wYi36SA5cZ3s5binMPMRlLasm6Aw" 

df_raw = load_data_from_drive(DRIVE_FILE_ID)

if df_raw.empty:
    st.warning("데이터를 불러오지 못했습니다. 구글 드라이브 파일의 공유 설정을 확인해 주세요.")
    st.stop()

# 이후 필터 및 탭 구성 로직 (기존 코드와 동일)
# ... (기존 코드 하단부) ...

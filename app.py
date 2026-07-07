import streamlit as st
import os
import base64
import re

# --- 1. 웹 UI 기본 설정 ---
st.set_page_config(page_title="FST to AUPRESET Converter", page_icon="🎵", layout="centered")

# --- (새로 추가) 이미지 Base64 변환 함수 ---
# 로컬 이미지를 HTML 안에서 띄우기 위해 변환하는 함수입니다.
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        return ""

# 사용법 이미지 파일 이름 지정 (준비하신 이미지 이름으로 변경하세요)
guide_image_base64 = get_base64_image("guide.png")

# --- 2. 다크 모드 전용 배경 및 텍스트 CSS ---
st.markdown(f"""
    <style>
    /* 기존 배경 및 텍스트 설정 */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #0E1117 !important;
        background-image: 
            radial-gradient(at 10% 20%, rgba(47, 165, 114, 0.15) 0px, transparent 40%),
            radial-gradient(at 90% 80%, rgba(138, 43, 226, 0.12) 0px, transparent 40%) !important;
        background-attachment: fixed !important;
    }}
    .desc-text {{ font-size: 16px; color: #A0A0A0 !important; }}
    .warn-text {{ font-size: 14px; color: #5CC2F2 !important; line-height: 1.6; font-weight: 500; }}
    .credit-text {{ text-align: center; font-size: 12px; color: #606060 !important; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}

    /* ---------------------------------------------------
       [새로 추가됨] How to use 슬라이드 패널 CSS 
       --------------------------------------------------- */
    /* 숨겨진 체크박스 (작동 트리거 역할) */
    #help-toggle {{ display: none; }}

    /* How to use 버튼 디자인 */
    .help-btn {{
        display: inline-block;
        width: 100%;
        text-align: center;
        padding: 8px 16px;
        background-color: transparent;
        color: #A0A0A0;
        border: 1px solid #444;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s;
    }}
    .help-btn:hover {{ background-color: rgba(255,255,255,0.1); color: white; }}

    /* 슬라이드 패널 (서랍) 디자인 */
    .help-drawer {{
        position: fixed;
        top: 0;
        right: -450px; /* 처음엔 화면 오른쪽 밖으로 숨김 */
        width: 400px;
        max-width: 90vw;
        height: 100vh;
        background-color: #1a1c24;
        box-shadow: -5px 0 25px rgba(0,0,0,0.8);
        z-index: 999999;
        transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* 부드러운 감속 애니메이션 */
        padding: 30px 20px;
        overflow-y: auto;
    }}
    
    /* 체크박스가 체크되면 서랍이 스르륵 나옴 */
    #help-toggle:checked ~ .help-drawer {{
        right: 0; 
    }}

    /* 어두운 배경 오버레이 */
    .overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(2px);
        z-index: 999998;
        opacity: 0;
        visibility: hidden;
        transition: all 0.4s ease;
    }}
    #help-toggle:checked ~ .overlay {{
        opacity: 1;
        visibility: visible;
    }}

    /* 닫기 버튼(X) */
    .close-btn {{
        color: #A0A0A0;
        font-size: 28px;
        cursor: pointer;
        float: right;
        margin-top: -10px;
        transition: color 0.2s;
    }}
    .close-btn:hover {{ color: #FF4B4B; }}
    </style>

    <!-- HTML 구조 주입 (체크박스, 오버레이, 서랍 본체) -->
    <input type="checkbox" id="help-toggle">
    <label for="help-toggle" class="overlay"></label>
    
    <div class="help-drawer">
        <label for="help-toggle" class="close-btn">×</label>
        <h3 style="color: white; margin-top: 0; margin-bottom: 20px;">How to use?</h3>
        <!-- 파이썬에서 불러온 Base64 이미지를 이곳에 출력 -->
        <img src="data:image/png;base64,{guide_image_base64}" alt="Guide" style="width: 100%; border-radius: 8px;">
    </div>
""", unsafe_allow_html=True)

# --- 3. 언어 상태(세션) 초기화 ---
if 'lang' not in st.session_state:
    headers = st.context.headers
    accept_language = headers.get("Accept-Language", "en")
    if "ko" in accept_language.lower():
        st.session_state.lang = "KOR"
    else:
        st.session_state.lang = "ENG"

# --- 4. 상단 버튼 배치 (도움말 버튼 + 언어 토글) ---
# 공간을 3개로 나누어 깔끔하게 배치합니다.
col1, col2, col3 = st.columns([7, 1.5, 1.5]) 

with col2:
    # 스트림릿 버튼 대신 CSS로 만든 HTML 버튼 라벨을 삽입합니다.
    st.markdown('<label for="help-toggle" class="help-btn">❓ Help</label>', unsafe_allow_html=True)

with col3:
    if st.session_state.lang == "KOR":
        if st.button("🌐 ENG", use_container_width=True):
            st.session_state.lang = "ENG"
            st.rerun()
    else:
        if st.button("🌐 KOR", use_container_width=True):
            st.session_state.lang = "KOR"
            st.rerun()

# ... (이 아래로는 기존 5. 다국어 텍스트 데이터 사전 부터 끝까지 동일합니다) ...

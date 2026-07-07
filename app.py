import streamlit as st
import os

# --- 1. 웹 UI 기본 설정 ---
st.set_page_config(page_title="FST to AUPRESET Converter", page_icon="🎵", layout="centered")

# --- 2. 다크 모드 전용 배경 및 텍스트 CSS ---
st.markdown("""
    <style>
    /* 전체 배경에 은은한 블러 그라데이션 적용 (다크 모드 베이스) */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #0E1117 !important;
        background-image: 
            radial-gradient(at 10% 20%, rgba(47, 165, 114, 0.15) 0px, transparent 40%),
            radial-gradient(at 90% 80%, rgba(138, 43, 226, 0.12) 0px, transparent 40%) !important;
        background-attachment: fixed !important;
    }
    
    /* 텍스트 색상 클래스 */
    .desc-text { font-size: 16px; color: #A0A0A0 !important; }
    .warn-text { font-size: 14px; color: #5CC2F2 !important; line-height: 1.6; font-weight: 500; }
    .credit-text { text-align: center; font-size: 12px; color: #606060 !important; }
    
    /* 상단 기본 헤더바 투명화 */
    [data-testid="stHeader"] { background: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 언어 상태(세션) 초기화 ---
if 'lang' not in st.session_state:
    headers = st.context.headers
    accept_language = headers.get("Accept-Language", "en")
    
    if "ko" in accept_language.lower():
        st.session_state.lang = "KOR"
    else:
        st.session_state.lang = "ENG"

# --- 4. 우측 상단 언어 토글 버튼 배치 ---
col1, col2 = st.columns([8.5, 1.5])
with col2:
    if st.session_state.lang == "KOR":
        if st.button("🌐 ENG", use_container_width=True):
            st.session_state.lang = "ENG"
            st.rerun()
    else:
        if st.button("🌐 KOR", use_container_width=True):
            st.session_state.lang = "KOR"
            st.rerun()

# --- 5. 다국어 텍스트 데이터 사전 ---
if st.session_state.lang == "KOR":
    text = {
        "title": "ShaperBox 3 프리셋 변환기 (Logic)",
        "desc": "FL Studio의 .fst 프리셋을 Logic Pro의 .aupreset 포맷으로 변환합니다.",
        "warn": "⚠️ 주의: ShaperBox 3 하나만 단독으로 로드된 프리셋을 사용해 주세요.",
        "upload": ".fst 파일들을 선택하거나 드래그 앤 드롭하세요",
        "result": "### 변환 결과",
        "download": "⬇️ {filename} 다운로드",
        "error_no_vst": "'{filename}' 파일에서 Mac/Logic용 프리셋 데이터를 찾을 수 없습니다."
    }
else:
    text = {
        "title": "ShaperBox 3 Preset Converter (Logic)",
        "desc": "Convert FL Studio .fst presets to Logic Pro .aupreset format.",
        "warn": "⚠️ Note: Please ensure that the preset only has a single instance of ShaperBox 3 loaded.",
        "upload": "Drag and drop or select .fst files",
        "result": "### Conversion Results",
        "download": "⬇️ Download {filename}",
        "error_no_vst": "Could not find Mac/Logic preset data in '{filename}'."
    }

# --- 6. 핵심 변환 로직 함수 (Logic 전용) ---
def process_fst_to_aupreset(fst_bytes):
    # FST 파일 내부에서 로직(Mac)용 plist XML 데이터의 시작과 끝을 찾습니다.
    start_marker = b'<?xml version="1.0"'
    end_marker = b'</plist>'
    
    start_idx = fst_bytes.find(start_marker)
    end_idx = fst_bytes.find(end_marker)
    
    # XML 데이터를 찾지 못하면 변환 실패 처리
    if start_idx == -1 or end_idx == -1:
        return None
        
    # 시작점부터 끝점(</plist> 글자 길이 포함)까지 텍스트만 정확하게 잘라냅니다.
    aupreset_bytes = fst_bytes[start_idx:end_idx + len(end_marker)]
    
    return aupreset_bytes

# --- 7. 메인 화면 렌더링 ---
st.title(text["title"])

# 설명 텍스트
st.markdown(f"<div class='desc-text'>{text['desc']}</div>", unsafe_allow_html=True)
st.write("")

# 주의 문구
st.markdown(f"<div class='warn-text'>{text['warn']}</div>", unsafe_allow_html=True)
st.write("")

# 파일 업로더
uploaded_files = st.file_uploader(text["upload"], type=['fst'], accept_multiple_files=True)

# 파일 처리 및 다운로드 버튼
if uploaded_files:
    st.write(text["result"])
    
    for uploaded_file in uploaded_files:
        fst_bytes = uploaded_file.read()
        preset_data = process_fst_to_aupreset(fst_bytes)
        
        if preset_data:
            base_name = os.path.splitext(uploaded_file.name)[0]
            preset_filename = f"{base_name}.aupreset"
            
            st.download_button(
                label=text["download"].format(filename=preset_filename),
                data=preset_data,
                file_name=preset_filename,
                mime="application/xml"
            )
        else:
            st.warning(text["error_no_vst"].format(filename=uploaded_file.name))

# --- 8. 화면 맨 아래 서명(Credit) 추가 ---
st.markdown(
    """
    <br><br><br>
    <div class='credit-text'>
        @mamafosho
    </div>
    """, 
    unsafe_allow_html=True
)

import streamlit as st
import os
import base64
import re

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
        "error_no_vst": "'{filename}' 파일에서 VST 데이터를 찾을 수 없습니다.",
        "error_no_template": "서버에 template.aupreset 파일이 없습니다. 개발자에게 문의하세요."
    }
else:
    text = {
        "title": "ShaperBox 3 Preset Converter (Logic)",
        "desc": "Convert FL Studio .fst presets to Logic Pro .aupreset format.",
        "warn": "⚠️ Note: Please ensure that the preset only has a single instance of ShaperBox 3 loaded.",
        "upload": "Drag and drop or select .fst files",
        "result": "### Conversion Results",
        "download": "⬇️ Download {filename}",
        "error_no_vst": "Could not find VST data in '{filename}'.",
        "error_no_template": "template.aupreset not found on the server. Contact the developer."
    }

# --- 6. 핵심 변환 로직 함수 (Logic AUPRESET 용) ---
def process_fst_data(fst_bytes, template_xml):
    # 1. FST 파일에서 '#zip#' 시그니처 찾기 (플러그인 데이터 시작점)
    start_idx = fst_bytes.find(b'#zip#')
    if start_idx == -1:
        return None
        
    # 2. 시작점부터 끝까지 바이너리 데이터 추출
    vst_chunk_binary = fst_bytes[start_idx:]
    
    # 3. 추출한 바이너리 데이터를 Base64 규격으로 인코딩 (Apple XML 포맷에 맞춰 자동 줄바꿈)
    b64_str = base64.encodebytes(vst_chunk_binary).decode('utf-8')
    
    # 4. 정규식을 이용해 template.aupreset 내의 <key>jucePluginState</key> 하위 <data> 영역을 방금 만든 b64_str로 덮어쓰기
    pattern = re.compile(r'(<key>jucePluginState</key>\s*<data>)(.*?)(</data>)', re.DOTALL)
    final_xml = pattern.sub(r'\g<1>\n' + b64_str + r'\g<3>', template_xml)
    
    return final_xml

# --- 7. 메인 화면 렌더링 ---
st.title(text["title"])

# 설명 텍스트
st.markdown(f"<div class='desc-text'>{text['desc']}</div>", unsafe_allow_html=True)
st.write("")

# 주의 문구
st.markdown(f"<div class='warn-text'>{text['warn']}</div>", unsafe_allow_html=True)
st.write("")

# 템플릿 로드 (Logic 버전)
template_path = 'template.aupreset'
try:
    with open(template_path, 'r', encoding='utf-8') as f:
        template_xml = f.read()
except FileNotFoundError:
    st.error(text["error_no_template"])
    st.stop()

# 파일 업로더
uploaded_files = st.file_uploader(text["upload"], type=['fst'], accept_multiple_files=True)

# 파일 처리 및 다운로드 버튼
if uploaded_files:
    st.write(text["result"])
    
    for uploaded_file in uploaded_files:
        fst_bytes = uploaded_file.read()
        final_xml = process_fst_data(fst_bytes, template_xml)
        
        if final_xml:
            base_name = os.path.splitext(uploaded_file.name)[0]
            # 압축(gzip) 없이 순수 XML 텍스트 포맷으로 aupreset 다운로드
            aupreset_filename = f"{base_name}.aupreset"
            
            st.download_button(
                label=text["download"].format(filename=aupreset_filename),
                data=final_xml.encode('utf-8'),
                file_name=aupreset_filename,
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

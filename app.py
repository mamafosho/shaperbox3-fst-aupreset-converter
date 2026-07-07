import streamlit as st
import os
import base64
import re

# --- 1. 웹 UI 기본 설정 ---
st.set_page_config(page_title="FST to AUPRESET Converter", page_icon="🎵", layout="centered")

# --- 2. 이미지 Base64 변환 함수 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        return ""

guide_image_base64 = get_base64_image("guide.png")

# --- 3. 언어 상태(세션) 초기화 ---
if 'lang' not in st.session_state:
    headers = st.context.headers
    accept_language = headers.get("Accept-Language", "en")
    
    if "ko" in accept_language.lower():
        st.session_state.lang = "KOR"
    else:
        st.session_state.lang = "ENG"

# --- 4. 다국어 텍스트 데이터 사전 ---
if st.session_state.lang == "KOR":
    text = {
        "title": "ShaperBox 3 프리셋 변환기 (Logic)",
        "desc": "FL Studio의 .fst 프리셋을 Logic Pro의 .aupreset 포맷으로 변환합니다.",
        "warn": "⚠️ 주의: ShaperBox 3 하나만 단독으로 로드된 프리셋을 사용해 주세요.",
        "upload": ".fst 파일들을 선택하거나 드래그 앤 드롭하세요",
        "result": "### 변환 결과",
        "download": "⬇️ {filename} 다운로드",
        "error_no_vst": "'{filename}' 파일에서 VST 데이터를 찾을 수 없습니다.",
        "error_no_template": "서버에 template.aupreset 파일이 없습니다. 개발자에게 문의하세요.",
        "help_title": "사용 방법",
        "help_desc": "로직에서 쉐이퍼박스3키고 사진대로 로드하면되고 밑에 저장 눌러놓으면 AU presets에서 다음부터 바로 불러오기가능"
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
        "error_no_template": "template.aupreset not found on the server. Contact the developer.",
        "help_title": "How to use",
        "help_desc": "you can also press save button and load it from AU Presets"
    }

# --- 5. 다크 모드 전용 배경, 텍스트 및 서랍 UI CSS ---
st.markdown(f"""
    <style>
    /* 전체 배경 은은한 블러 그라데이션 */
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

    /* How to use 슬라이드 패널 CSS */
    #help-toggle {{ display: none; }}
    .help-btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        min-height: 38.4px; 
        background-color: transparent;
        color: #FAFAFA;
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 400;
        transition: all 0.2s ease;
    }}
    .help-btn:hover {{ 
        border-color: #FF4B4B; 
        color: #FF4B4B; 
    }}
    .help-drawer {{
        position: fixed;
        top: 0;
        right: -450px; 
        width: 400px;
        max-width: 90vw;
        height: 100vh;
        background-color: #1a1c24;
        box-shadow: -5px 0 25px rgba(0,0,0,0.8);
        z-index: 999999;
        transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
        padding: 30px 20px;
        overflow-y: auto;
    }}
    #help-toggle:checked ~ .help-drawer {{
        right: 0; 
    }}
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
    <input type="checkbox" id="help-toggle">
    <label for="help-toggle" class="overlay"></label>
    <div class="help-drawer">
        <label for="help-toggle" class="close-btn">×</label>
        <h3 style="color: white; margin-top: 0; margin-bottom: 20px;">{text['help_title']}</h3>
        <img src="data:image/png;base64,{guide_image_base64}" alt="Guide" style="width: 100%; border-radius: 8px;">
        <div style="color: #A0A0A0; font-size: 14px; margin-top: 15px; line-height: 1.6; word-break: keep-all;">
            {text['help_desc']}
        </div>
    </div>
""", unsafe_allow_html=True)


# --- 6. 상단 버튼 배치 (도움말 버튼 + 언어 토글) ---
col1, col2, col3 = st.columns([7.5, 1.3, 1.2]) 

with col2:
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

# --- 7. 핵심 변환 로직 함수 (Logic AUPRESET 용) ---
def process_fst_data(fst_bytes, template_xml):
    start_idx = fst_bytes.find(b'#zip#')
    if start_idx == -1:
        return None
        
    vst_chunk_binary = fst_bytes[start_idx:]
    b64_str = base64.encodebytes(vst_chunk_binary).decode('utf-8')
    
    pattern = re.compile(r'(<key>jucePluginState</key>\s*<data>)(.*?)(</data>)', re.DOTALL)
    final_xml = pattern.sub(r'\g<1>\n' + b64_str + r'\g<3>', template_xml)
    
    return final_xml

# --- 8. 메인 화면 렌더링 ---
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
            aupreset_filename = f"{base_name}.aupreset"
            
            st.download_button(
                label=text["download"].format(filename=aupreset_filename),
                data=final_xml.encode('utf-8'),
                file_name=aupreset_filename,
                mime="application/xml"
            )
        else:
            st.warning(text["error_no_vst"].format(filename=uploaded_file.name))

# --- 9. 화면 맨 아래 서명(Credit) 추가 ---
st.markdown(
    """
    <br><br><br>
    <div class='credit-text'>
        @mamafosho
    </div>
    """, 
    unsafe_allow_html=True
)

import streamlit as st
from modules import ui_components, wardrobe

# 1. Page Configuration
st.set_page_config(
    page_title="FashionFrenzy - AI Style Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS for Futuristic Elegant UI
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global styles */
    .stApp {
        background: #0a0a0a;
        color: #fff;
    }
    
    /* Animated gradient background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(255, 0, 110, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(131, 56, 236, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(6, 255, 165, 0.1) 0%, transparent 50%);
        z-index: 0;
        pointer-events: none;
        animation: gradientShift 20s ease infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.1); }
    }
    
    /* Grid overlay */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 50px 50px;
        z-index: 0;
        pointer-events: none;
    }
    
    /* Main container */
    .main > div {
        position: relative;
        z-index: 1;
    }
    
    /* Logo/Header styling */
    .logo-container {
        text-align: center;
        padding: 40px 0 50px 0;
        margin-bottom: 30px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .logo-text {
        font-size: 5rem;
        font-weight: 900;
        letter-spacing: 0.15em;
        background: linear-gradient(45deg, #ff006e, #8338ec, #06ffa5, #ff006e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        background-size: 200% 100%;
        animation: shimmer 4s linear infinite;
        margin: 0;
        padding: 0;
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .tagline {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.6);
        letter-spacing: 0.3em;
        text-transform: uppercase;
        margin-top: 15px;
    }
    
    /* API Key Welcome Screen */
    .welcome-container {
        max-width: 600px;
        margin: 100px auto;
        padding: 50px;
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(131, 56, 236, 0.3);
        border-radius: 25px;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 60px rgba(131, 56, 236, 0.3);
        text-align: center;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(45deg, #ff006e, #8338ec, #06ffa5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    
    .welcome-subtitle {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 30px;
        letter-spacing: 0.1em;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: #fff !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Column styling */
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px !important;
        backdrop-filter: blur(10px);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(131, 56, 236, 0.5);
        border-radius: 15px;
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(131, 56, 236, 0.8);
        background: rgba(131, 56, 236, 0.1);
        transform: translateY(-2px);
    }
    
    /* Buttons */
    .stButton > button {
        background: transparent;
        border: 2px solid #fff;
        color: #fff;
        padding: 12px 30px;
        font-size: 0.85rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 600;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff006e, #8338ec);
        border-color: transparent;
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(131, 56, 236, 0.5);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff006e, #8338ec, #06ffa5);
        border: none;
        box-shadow: 0 5px 20px rgba(255, 0, 110, 0.4);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #06ffa5, #8338ec, #ff006e);
        box-shadow: 0 10px 40px rgba(255, 0, 110, 0.6);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: #fff;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(131, 56, 236, 0.6);
        background: rgba(131, 56, 236, 0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #fff !important;
        font-weight: 600;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(131, 56, 236, 0.1);
        border-color: rgba(131, 56, 236, 0.5);
        transform: translateX(5px);
    }
    
    /* Container borders */
    [data-testid="stVerticalBlock"] > div:has(> div[data-testid="stImage"]) {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 15px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stVerticalBlock"] > div:has(> div[data-testid="stImage"]):hover {
        border-color: rgba(6, 255, 165, 0.5);
        box-shadow: 0 8px 25px rgba(6, 255, 165, 0.2);
        transform: translateY(-5px);
    }
    
    /* Images */
    img {
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    img:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.1);
    }
    
    /* Chat container */
    [data-testid="stChatMessageContainer"] {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stChatMessage"] {
        background: transparent !important;
        color: #ffffff !important;
    }
    
    /* User message */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, rgba(255, 0, 110, 0.3), rgba(131, 56, 236, 0.3)) !important;
        border-left: 4px solid #ff006e !important;
        padding: 15px !important;
        border-radius: 10px !important;
        margin: 8px 0 !important;
    }
    
    /* Assistant message */
    [data-testid="stChatMessage"]:not([data-testid*="user"]) {
        background: linear-gradient(135deg, rgba(6, 255, 165, 0.25), rgba(131, 56, 236, 0.25)) !important;
        border-left: 4px solid #06ffa5 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        margin: 8px 0 !important;
    }
    
    /* Chat message text - Force visibility */
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] h4,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] code,
    [data-testid="stChatMessage"] pre {
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
        font-weight: 500 !important;
    }
    
    /* Markdown content in chat */
    [data-testid="stChatMessage"] .stMarkdown {
        color: #ffffff !important;
    }
    
    [data-testid="stChatMessage"] .stMarkdown * {
        color: #ffffff !important;
    }
    
    /* Code blocks in chat */
    [data-testid="stChatMessage"] code {
        background: rgba(0, 0, 0, 0.5) !important;
        color: #06ffa5 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    
    [data-testid="stChatMessage"] pre {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    
    /* Chat input */
    .stChatInput > div {
        background: rgba(0, 0, 0, 0.9) !important;
        border: 2px solid rgba(131, 56, 236, 0.6) !important;
        border-radius: 25px;
        backdrop-filter: blur(10px);
    }
    
    .stChatInput > div:focus-within {
        border-color: rgba(131, 56, 236, 1) !important;
        box-shadow: 0 0 25px rgba(131, 56, 236, 0.6) !important;
        background: rgba(0, 0, 0, 0.95) !important;
    }
    
    .stChatInput textarea {
        color: #ffffff !important;
        background: transparent !important;
        font-weight: 500 !important;
        caret-color: #ffffff !important;
    }
    
    .stChatInput textarea::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 400 !important;
    }
    
    /* Force chat input text to be visible - Multiple selectors */
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInputTextArea"] textarea,
    .stChatInput textarea,
    div[data-baseweb="textarea"] textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Chat input container override */
    div[data-baseweb="base-input"] {
        background-color: rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Additional targeting for Streamlit's internal classes */
    [class*="stChatInput"] [class*="textarea"],
    [class*="stChatInput"] textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px;
        color: #fff !important;
        padding: 15px;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(131, 56, 236, 0.8) !important;
        box-shadow: 0 0 15px rgba(131, 56, 236, 0.3) !important;
        background: rgba(0, 0, 0, 0.7) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Success/Error/Info messages */
    .stSuccess, .stError, .stInfo, .stWarning {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        padding: 1rem;
    }
    
    .stSuccess {
        border-color: #06ffa5;
        background: rgba(6, 255, 165, 0.1);
    }
    
    .stError {
        border-color: #ff006e;
        background: rgba(255, 0, 110, 0.1);
    }
    
    .stInfo {
        border-color: #8338ec;
        background: rgba(131, 56, 236, 0.1);
    }
    
    /* Captions */
    .stCaption {
        color: rgba(255, 255, 255, 0.5) !important;
        letter-spacing: 0.05em;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
        margin: 30px 0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: rgba(131, 56, 236, 0.3);
        border-top-color: #8338ec;
    }
    
    /* Status container */
    [data-testid="stStatus"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Toast */
    [data-testid="stToast"] {
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid rgba(6, 255, 165, 0.5);
        border-radius: 10px;
        backdrop-filter: blur(20px);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff006e, #8338ec);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8338ec, #06ffa5);
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Label styling */
    label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# 3. API Key Management
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "chat_model" not in st.session_state:
    st.session_state.chat_model = "gemini-2.0-flash"
if "vton_model" not in st.session_state:
    st.session_state.vton_model = "models/nano-banana-pro-preview"
if "user_gender" not in st.session_state:
    st.session_state.user_gender = "Male"

# Available models
CHAT_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

VTON_MODELS = [
    "models/nano-banana-pro-preview",
    "gemini-2.0-flash-preview-image-generation",
    "imagen-3.0-generate-002",
]

if not st.session_state.gemini_api_key:
    # Elegant Welcome Screen
    st.markdown("""
    <div class="logo-container">
        <h1 class="logo-text">FASHIONFRENZY</h1>
        <p class="tagline">AI-Powered Style Studio</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">Welcome to FashionFrenzy</div>
        <div class="welcome-subtitle">Your Personal AI Fashion Curator</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔑 Enter your Gemini API Key to unlock your AI style assistant")
        api_key = st.text_input(
            "Gemini API Key", 
            type="password", 
            placeholder="Enter your API key here...",
            help="Get your key from https://aistudio.google.com/app/apikey",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🤖 Model Selection")
        
        # Chat Model Selection
        chat_model = st.selectbox(
            "💬 Style Assistant Model",
            options=CHAT_MODELS,
            index=0,
            help="Model for the chatbot/style assistant"
        )
        
        # VTON Model Selection
        vton_model = st.selectbox(
            "🪄 Virtual Try-On Model",
            options=VTON_MODELS,
            index=0,  # Default to Nano Banana
            help="Model for virtual try-on image generation"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Connect & Start Styling", type="primary", use_container_width=True):
            if api_key:
                st.session_state.gemini_api_key = api_key
                st.session_state.chat_model = chat_model
                st.session_state.vton_model = vton_model
                st.success("✨ Connected! Initializing your fashion studio...")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Please enter a valid API key.")
    st.stop()

# 4. Initialize Wardrobe Structure
wardrobe.init_wardrobe()

# 5. Main App Header
st.markdown("""
<div class="logo-container">
    <h1 class="logo-text">FASHIONFRENZY</h1>
    <p class="tagline">Intelligent Personalized Wardrobe Curator</p>
</div>
""", unsafe_allow_html=True)

# 6. Layout: 3 Columns
col_left, col_mid, col_right = st.columns([0.25, 0.45, 0.3], gap="medium")

with col_left:
    ui_components.render_left_column()

with col_mid:
    ui_components.render_middle_column()

with col_right:
    ui_components.render_right_column()

# 7. Footer
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 30px; color: rgba(255, 255, 255, 0.3); font-size: 0.75rem; letter-spacing: 0.15em;">
    © 2026 FASHIONFRENZY • AI-POWERED FASHION PLATFORM
</div>
""", unsafe_allow_html=True)
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Tech Helper", page_icon="🤝")

# --- CSS HACKS (The "True Center" Fix) ---
st.markdown("""
    <style>
    /* 1. Big Font */
    div[data-testid="stMarkdownContainer"] p { font-size: 22px !important; line-height: 1.6 !important; }
    div[data-testid="stMarkdownContainer"] li { font-size: 22px !important; margin-bottom: 10px !important; }
    
    /* 2. THE FIX: Centered Floating Audio */
    div[data-testid="stAudioInput"] {
        position: fixed;
        bottom: 80px; /* Sits above the text box */
        left: 50%;    /* Move to the middle of the screen */
        transform: translateX(-50%); /* Shift back to center perfectly */
        
        width: 90%;   /* Take up most of the screen on phones */
        max-width: 600px; /* Stop growing on big screens */
        
        z-index: 9999; /* Always on top */
        background-color: transparent;
        border: none;
    }
    
    /* Make the internal box look like a pill/button */
    div[data-testid="stAudioInput"] > div {
        background-color: #262730; /* Dark grey background */
        border-radius: 20px;
        border: 1px solid #444;
        padding: 5px;
    }

    /* Hide Label */
    div[data-testid="stAudioInput"] label { display: none; }
    
    /* 3. Add massive padding to bottom of chat so messages don't hide behind the mic */
    div[data-testid="stVerticalBlock"] {
        padding-bottom: 150px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KEY MANAGEMENT ---
if "GOOGLE_API_KEY" in st.secrets:
    # THIS LINE MUST BE INDENTED 4 SPACES
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# --- THE AI PERSONA ---
SYSTEM_PROMPT = """
You are a helpful, patient family friend helping an older relative with tech.
RULES:
1. G

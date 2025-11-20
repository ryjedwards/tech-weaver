import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Tech Helper", page_icon="🤝")

# --- CSS HACKS (The "Clean UI" Fix) ---
st.markdown("""
    <style>
    /* 1. Big Font for readability */
    div[data-testid="stMarkdownContainer"] p { font-size: 22px !important; line-height: 1.6 !important; }
    div[data-testid="stMarkdownContainer"] li { font-size: 22px !important; margin-bottom: 10px !important; }
    
    /* 2. CLEANER AUDIO RECORDER */
    div[data-testid="stAudioInput"] {
        position: fixed;
        bottom: 70px; /* Sits exactly on top of the text input */
        left: 0;
        width: 100%;
        z-index: 1000;
        background-color: transparent; /* No more white box */
        border: none; /* No more border */
        padding: 0px 20px; /* Align with text box */
    }
    
    /* Remove the default "Drag and drop" text to make it cleaner */
    div[data-testid="stAudioInput"] > div > div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Hide the label */
    div[data-testid="stAudioInput"] label {
        display: none;
    }
    
    /* 3. Adjust History to not hide behind the controls */
    div[data-testid="stVerticalBlock"] {
        padding-bottom: 150px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KEY MANAGEMENT ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# --- THE AI PERSONA ---
SYSTEM_PROMPT = """
You are a helpful, patient family friend helping an older relative with tech.
RULES:
1. GREETINGS: If user says "Hello", just say "Hello" back.
2. VALIDATE: Empathize with their frustration.
3. CHECKLIST: End with "✅ Steps to Try:".
4. TONE: Warm, respectful, NO JARGON.
"""

# --- MAIN APP LOGIC ---
st.title("🤝 Tech Helper")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Start Over"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

if not api_key:
    st.warning("Sleeping... (Missing API Key)")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- WELCOME MAT ---
welcome_placeholder = st.empty()
if len(st.session_state.messages) == 0:
    with welcome_placeholder.container():
        st.info("👋 **Hello!** \n\nTap the **Microphone** below to speak, or **Type** in the box.")

# --- HISTORY ---
history_container = st.container()
with history_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # Spacer
    st.markdown("<br><br><br>", unsafe_allow_html=True)

# --- INPUTS ---
audio_value = st.audio_input("Voice Input")
text_value = st.chat_input("Type here...")

# --- PROCESSING ---
user_message = None
is_audio = False

if audio_value and audio_value != st.session_state.last_audio:
    user_message = audio_value
    is_audio = True
    st.session_state.last_audio = audio_value
elif text_value:
    user_message = text_value
    is_audio = False

if user_message:
    welcome_placeholder.empty()

    if not is_audio:
        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)
    else:
        st.session_state.messages.append({"role": "user", "content": "🎤 *Voice Message Sent*"})
        with st.chat_message("user"):
            st.markdown("🎤 *Voice Message Sent*")

    with st.spinner("Thinking..."):
        try:
            if is_audio:
                audio_bytes = user_message.read()
                response = model.generate_content([
                    "If greeting, return greeting. Else help. End with checklist.",
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
            else:
                response = model.generate_content(user_message)
            
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text})
            with st.chat_message("assistant"):
                st.markdown(ai_text)

            # AUDIO AUTOPLAY
            sound_file = BytesIO()
            tts = gTTS(text=ai_text, lang='en', slow=False)
            tts.write_to_fp(sound_file)
            st.audio(sound_file, format='audio/mp3', start_time=0, autoplay=True)

        except Exception as e:
            st.error(f"Connection error: {e}")

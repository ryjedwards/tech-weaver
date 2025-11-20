import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Tech Helper", page_icon="🤝")

# --- CSS FOR BIG FONT ---
st.markdown("""
    <style>
    div[data-testid="stMarkdownContainer"] p { font-size: 22px !important; line-height: 1.6 !important; }
    div[data-testid="stMarkdownContainer"] li { font-size: 22px !important; margin-bottom: 10px !important; }
    .stChatInput textarea { font-size: 18px !important; }
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
STRUCTURE:
1. EMPATHY FIRST: Validate their feelings (e.g., "That is so frustrating").
2. EXPLANATION: Plain English.
3. THE CHECKLIST: End with a section "✅ Steps to Try:".
TONE: Warm, respectful, NO JARGON.
"""

# --- MAIN APP LOGIC ---
st.title("🤝 Tech Helper")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Controls")
    # The "Reset" Button
    if st.button("🔄 Start Over / Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.warning("Sleeping... (Missing API Key)")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUTS ---
audio_value = st.audio_input("Record your voice")
text_value = st.chat_input("Or type here...")

# --- PROCESSING ---
user_message = None
is_audio = False

if audio_value:
    user_message = audio_value
    is_audio = True
elif text_value:
    user_message = text_value
    is_audio = False

if user_message:
    if not is_audio:
        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)
    else:
        # We don't save the audio file to history to keep it fast, just a placeholder
        st.session_state.messages.append({"role": "user", "content": "🎤 *Voice Message Sent*"})
        with st.chat_message("user"):
            st.markdown("🎤 *Voice Message Sent*")

    with st.spinner("Thinking..."):
        try:
            if is_audio:
                audio_bytes = user_message.read()
                response = model.generate_content([
                    "Listen and help. End with a checklist.",
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

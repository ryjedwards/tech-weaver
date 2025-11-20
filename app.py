import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Tech Helper", page_icon="🤝")

# --- CSS HACKS (The Visual Magic) ---
# 1. Big Font
# 2. STICKY AUDIO: This forces the microphone to float at the bottom!
st.markdown("""
    <style>
    /* Big Font for readability */
    div[data-testid="stMarkdownContainer"] p { font-size: 22px !important; line-height: 1.6 !important; }
    div[data-testid="stMarkdownContainer"] li { font-size: 22px !important; margin-bottom: 10px !important; }
    
    /* Floating Audio Recorder - This moves it to the bottom right */
    div[data-testid="stAudioInput"] {
        position: fixed;
        bottom: 100px; /* Sits right above the chat bar */
        z-index: 1000;
        width: 100%;
        max-width: 800px; /* Keeps it from getting too wide on desktop */
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    /* Hide the default label to make it cleaner */
    div[data-testid="stAudioInput"] label {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KEY MANAGEMENT ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# --- THE AI PERSONA (Updated to stop hallucinating) ---
SYSTEM_PROMPT = """
You are a helpful, patient family friend helping an older relative with tech.

CRITICAL RULES:
1. GREETINGS: If the user just says "Hello" or "Hi", JUST SAY HELLO BACK. Ask "What is going on?" DO NOT invent a problem.
2. BACKGROUND NOISE: If you hear silence or noise but no words, say "I couldn't quite hear you. Can you try again?"
3. EMPATHY FIRST: If they state a problem, validate their feelings.
4. THE CHECKLIST: End with a section "✅ Steps to Try:".
5. TONE: Warm, respectful, NO JARGON.
"""

# --- MAIN APP LOGIC ---
st.title("🤝 Tech Helper")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Start Over / Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None # Clear audio memory too
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
        st.info("👋 **Hello!** \n\nTap the **Microphone** at the bottom to speak, or **Type** below.")

# --- DISPLAY HISTORY ---
# We create a container for history so it stays ABOVE the fixed audio button
history_container = st.container()
with history_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # Add some empty space at the bottom so the last message isn't hidden by the mic
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# --- INPUTS ---
# We place these at the bottom of the script, but CSS moves them visually
audio_value = st.audio_input("Voice Input") # Label hidden by CSS
text_value = st.chat_input("Type here...")

# --- PROCESSING ---
user_message = None
is_audio = False

# Logic to prevent looping
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
                # We updated the prompt here to be stricter about "Just Hello"
                response = model.generate_content([
                    "If this is just a greeting, greet back. If it's a problem, help.",
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

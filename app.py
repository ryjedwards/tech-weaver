import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Tech Helper", page_icon="🤝")

# --- KEY MANAGEMENT ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# --- THE AI PERSONA ---
SYSTEM_PROMPT = """
You are a helpful, patient family friend who is good with technology. 
You are helping an older relative fix a tech problem.

TONE GUIDELINES:
1. EMPATHETIC: "That sounds annoying, let's fix it."
2. RESPECTFUL: Never talk down to them.
3. SIMPLE: No jargon. Keep it short (2-3 sentences max).
4. SAFETY: If hardware is broken, tell them to call a relative.
"""

# --- MAIN APP LOGIC ---
st.title("🤝 Tech Helper")
st.write("Tell me what is wrong, and I will say the answer out loud.")

if not api_key:
    st.warning("Sleeping... (Missing API Key)")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)

# --- INPUTS ---
col1, col2 = st.columns([4, 1])
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
    with st.spinner("Thinking..."):
        try:
            # 1. Get AI Text
            if is_audio:
                audio_bytes = user_message.read()
                response = model.generate_content([
                    "Listen and help like a friend.",
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
            else:
                response = model.generate_content(user_message)
            
            ai_text = response.text
            
            # Show text (optional, but good for reading along)
            st.markdown(f"**Answer:** {ai_text}")

            # 2. Convert to Speech
            sound_file = BytesIO()
            tts = gTTS(text=ai_text, lang='en', slow=False)
            tts.write_to_fp(sound_file)
            
            # 3. AUTO-PLAY AUDIO
            # The 'autoplay=True' flag is the magic switch here
            st.audio(sound_file, format='audio/mp3', start_time=0, autoplay=True)

        except Exception as e:
            st.error(f"Connection error: {e}")

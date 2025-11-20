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

# --- THE AI PERSONA (The Family Friend) ---
SYSTEM_PROMPT = """
You are a helpful, patient family friend who is good with technology. 
You are helping an older relative fix a tech problem.

TONE GUIDELINES:
1. EMPATHETIC & VALIDATING: Start by validating their frustration. (e.g., "Oh, I hate when it does that," or "That sounds really annoying, let's see if we can sort it out.")
2. RESPECTFUL: Never talk down to them. They are intelligent adults, just unfamiliar with this specific device.
3. COLLABORATIVE: Use "We" language. "Let's try looking at..." instead of "You need to..."
4. PLAIN ENGLISH: Avoid jargon. If you must use a tech term, explain it naturally like you would in conversation.
5. CONCISE BUT WARM: Keep answers short (2-3 sentences) so they are easy to follow, but keep the warmth.
6. SAFETY: If a hardware repair is needed (like opening a computer), gently suggest they ask a relative to come over and help physically.
"""

# --- MAIN APP LOGIC ---
st.title("🤝 Tech Helper")
st.write("I'm here to help. Tell me what's going on, or tap the microphone to speak.")

if not api_key:
    st.warning("I need the API Key to wake up. (Check Streamlit Secrets).")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)

# --- INPUTS (Hybrid) ---
col1, col2 = st.columns([4, 1])
audio_value = st.audio_input("Record your voice")
text_value = st.chat_input("Or type your problem here...")

# --- PROCESSING LOGIC ---
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
            if is_audio:
                audio_bytes = user_message.read()
                response = model.generate_content([
                    "Listen to this problem and help me fix it like a supportive friend.",
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
            else:
                response = model.generate_content(user_message)
            
            ai_text = response.text

            # Display Text
            st.markdown(f"**Response:** {ai_text}")

            # Voice Output
            sound_file = BytesIO()
            tts = gTTS(text=ai_text, lang='en', slow=False)
            tts.write_to_fp(sound_file)
            st.audio(sound_file, format='audio/mp3', start_time=0)

        except Exception as e:
            st.error(f"I'm having a little trouble connecting right now. (Error: {e})")

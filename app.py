import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="The Tech Weaver", page_icon="🧶")

# --- KEY MANAGEMENT ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# --- THE AI PERSONA ---
SYSTEM_PROMPT = """
You are "The Tech Weaver," a kind, wise, and comforting troubleshooter for elderly people.
1. VOICE: Speak like a calm storyteller. Keep answers SHORT (2-3 sentences max) so they are easy to listen to.
2. METAPHORS: Use simple analogies (e.g., "The internet pipe is clogged").
3. SAFETY: NEVER suggest opening devices. If it sounds like a hardware break, tell them to call a relative.
4. TONE: Extremely patient. 
"""

# --- MAIN APP LOGIC ---
st.title("🧶 The Tech Weaver")
st.write("Tap the microphone, ask your question, and wait for the Weaver to speak.")

if not api_key:
    st.warning("The Weaver is sleeping. (API Key missing).")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)

# --- VOICE INPUT ---
# This creates the microphone button
audio_value = st.audio_input("Record your question")

if audio_value:
    # 1. User has recorded something
    with st.spinner("The Weaver is listening..."):
        try:
            # 2. Send the AUDIO directly to Gemini (Multimodal)
            # We read the bytes from the recording
            audio_bytes = audio_value.read()
            
            # We send a prompt + the audio data
            response = model.generate_content([
                "Listen to this user's tech problem and respond kindly.",
                {
                    "mime_type": "audio/wav",
                    "data": audio_bytes
                }
            ])
            
            ai_text = response.text

            # 3. Display the text version
            st.markdown(f"**The Weaver says:** {ai_text}")

            # 4. Convert AI text to Speech (TTS)
            sound_file = BytesIO()
            tts = gTTS(text=ai_text, lang='en', slow=False)
            tts.write_to_fp(sound_file)
            
            # 5. Play the audio automatically
            st.audio(sound_file, format='audio/mp3', start_time=0)

        except Exception as e:
            st.error(f"The Weaver couldn't hear you clearly. (Error: {e})")

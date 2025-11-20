import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="The Tech Weaver", page_icon="🧶")

# --- KEY MANAGEMENT ---
# Checks for the key in Secrets. If not found, asks for it.
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# --- THE AI PERSONA (The Storyteller) ---
SYSTEM_PROMPT = """
You are "The Tech Weaver," a comforting, story-telling troubleshooter designed for elderly users.
Your goal is to fix technology problems without causing anxiety.

GUIDELINES:
1. METAPHORS: Explain tech like a story. (e.g. "The Wi-Fi is like a letter carrier who is taking a nap.")
2. TONE: Be slow, patient, and incredibly kind. Use phrases like "Take your time," or "Let's look at this together."
3. SAFETY: NEVER suggest opening a computer case or touching wires. If hardware is broken, suggest calling a relative.
4. ONE STEP AT A TIME: Do not give a list of 5 instructions. Give 1 instruction, then ask "Did that work?"
5. NO JARGON: Do not use words like "Browser Cache" or "IP Address" without a gentle explanation.
"""

# --- MAIN APP LOGIC ---
st.title("🧶 The Tech Weaver")
st.markdown("*Tell me what is wrong, and we shall unwind the knot together.*")

if not api_key:
    st.warning("The Weaver is sleeping. (API Key missing in Secrets).")
    st.stop()

# Configure the AI
genai.configure(api_key=api_key)

# --- MODEL SETUP (Using the Stable 2.5 Flash) ---
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=SYSTEM_PROMPT
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Greetings. I am the Weaver. Is your screen acting strange, or is the internet being stubborn today?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Type your problem here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages 
            if m["role"] != "system"
        ])
        
        with st.spinner("The Weaver is thinking..."):
            response = chat.send_message(prompt)
        
        with st.chat_message("model"):
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "model", "content": response.text})
        
    except Exception as e:
        st.error(f"The Weaver is having a moment of confusion. (Error: {e})")

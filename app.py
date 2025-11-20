import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
# This sets up the page title and icon
st.set_page_config(page_title="The Tech Weaver", page_icon="🧶")

# --- SIDEBAR (For your API Key) ---
with st.sidebar:
    st.header("⚙️ Setup")
    st.write("To wake the Weaver, please enter your Gemini API Key below.")
    # You can get a key for free at aistudio.google.com
    api_key = st.text_input("Gemini API Key", type="password")
    st.info("Don't have a key? [Get one free here](https://aistudio.google.com/app/apikey)")

# --- THE AI PERSONA ---
# This is the "System Instruction" that makes it safe and poetic.
SYSTEM_PROMPT = """
You are "The Tech Weaver," a kind, patient, and wise troubleshooter who helps elderly people with technology.
Your personality:
1. CALM & POETIC: You explain tech issues using metaphors (e.g., "Your internet is like a garden hose that has a small kink").
2. STORYTELLER: You frame solutions as a gentle journey. "Let us walk together to the Start Menu..."
3. SAFETY FIRST: NEVER suggest opening a physical device, soldering, or touching wires. If a physical repair is needed, tell them to call a professional relative.
4. NO JARGON: Do not use words like "Latency," "BIOS," or "Terminal" without explaining them simply first.
5. EFFECTUAL: While poetic, you must still solve the problem step-by-step. Ask one question at a time.
"""

# --- MAIN APP LOGIC ---
st.title("🧶 The Tech Weaver")
st.caption("A gentle guide for your technology troubles.")

if not api_key:
    st.warning("Please enter your API Key in the sidebar to begin.")
    st.stop()

# Configure the AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp", # Using the fast, latest model
    system_instruction=SYSTEM_PROMPT
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Greetings. I am the Weaver. Tell me, what device is troubling you today? Is it the glowing screen, or perhaps the magic typewriter?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Describe the problem here..."):
    # 1. Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate AI response
    try:
        # We create a chat session with the history
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages 
            if m["role"] != "system"
        ])
        
        response = chat.send_message(prompt)
        
        # 3. Display AI response
        with st.chat_message("model"):
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "model", "content": response.text})
        
    except Exception as e:
        st.error(f"The Weaver is having trouble thinking right now. (Error: {e})")

import streamlit as st
import google.generativeai as genai

st.title("🔧 The Weaver's Diagnostic Tool")

# 1. Check if the Key exists
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ API Key found in Secrets.")
else:
    st.error("❌ No API Key found! Please check Streamlit Secrets.")
    st.stop()

# 2. Try to connect to Google
genai.configure(api_key=api_key)

st.write("Attempting to contact Google's servers...")

try:
    # 3. Ask Google for a list of available models
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)

    if available_models:
        st.success("✅ SUCCESS! Your API Key is working.")
        st.write("### The following models are available to you:")
        # This prints the exact list of names we can use
        st.code("\n".join(available_models))
        
        st.info("👉 Look at the list above. Copy one of the names (like 'models/gemini-1.5-flash') exactly.")
    else:
        st.warning("⚠️ Connection worked, but no models were found. This usually means the API Key is restricted.")

except Exception as e:
    st.error(f"❌ Connection Failed. Error details below:")
    st.code(e)

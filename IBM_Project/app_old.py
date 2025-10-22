import streamlit as st
import google.generativeai as genai
import time
import random

# --- Page Configuration ---
st.set_page_config(
    page_title="Aura - Mental Health Companion",
    page_icon="💖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- API Key Configuration ---
# This securely loads the API key from Streamlit's secrets management
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except (KeyError, AttributeError):
    st.error("🔑 Gemini API Key not found. Please add it to your Streamlit secrets.", icon="🚨")
    st.stop()

# --- System Prompt and Model Configuration ---
# This prompt defines the chatbot's persona and instructions.
SYSTEM_PROMPT = """
You are "Aura," a compassionate and empathetic Mental Health Companion chatbot. Your purpose is to provide a safe, non-judgmental space for students to express their feelings.

Your Core Directives:
1.  **Detect Mood**: First, analyze the user's message to identify their sentiment (e.g., stressed, anxious, happy, lonely, neutral).
2.  **Empathetic Response**: Always start by validating the user's feelings. Use phrases like "It sounds like you're going through a lot," "Thank you for sharing that with me," or "It's completely understandable to feel that way."
3.  **Provide Support**: Offer gentle, supportive, and motivational feedback. If the user is struggling, provide one relevant, simple, and actionable relaxation tip or technique (like a breathing exercise, a grounding technique, or a mindfulness tip).
4.  **Maintain a Safe Tone**: Your tone must always be warm, calming, and positive. You are not a licensed therapist.
5.  **Safety First**: **Crucially, if the user expresses thoughts of self-harm, immediate danger, or severe crisis, you must immediately provide the following disclaimer and resources, without offering any other advice**: "It sounds like you are in significant distress. It's vital to talk to a professional right away. You can connect with people who can support you by calling or texting 988 anytime in the US and Canada. In the UK, you can call 111. These services are free, confidential, and available 24/7. Please reach out to them."
6.  **Do Not Diagnose**: Never attempt to diagnose any condition or provide medical advice. Always gently guide users towards professional help for serious issues.
"""

# Model configuration
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# --- Session State Initialization ---
# This ensures that the chat history is maintained across user interactions.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- Helper Functions for Impactful Features ---
def stream_typing_effect(text):
    """Creates a typewriter effect for the chatbot's responses."""
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

def get_random_thought():
    """Returns a random uplifting thought."""
    thoughts = [
        "It's okay not to be okay. Take your time.",
        "Every small step forward is still a step forward.",
        "You are more resilient than you think.",
        "Allow yourself a moment of stillness.",
        "The sun will rise, and we will try again."
    ]
    return random.choice(thoughts)

# --- Sidebar for Tools & Resources (Impactful Feature) ---
with st.sidebar:
    st.title("💖 Aura")
    st.markdown("Your safe space to talk.")
    st.divider()

    st.header("✨ Guided Exercises")
    with st.expander("🧘‍♀️ Guided Breathing"):
        st.markdown("""
        **Find a quiet place.**
        1.  **Inhale deeply** through your nose for a count of 4.
        2.  **Hold your breath** for a count of 7.
        3.  **Exhale slowly** through your mouth for a count of 8.
        4.  Repeat this cycle 3-5 times.
        """)
        if st.button("Start Breathing Exercise"):
            placeholder = st.empty()
            for i in range(3):
                placeholder.info("Breathe in...", icon="😮‍💨")
                time.sleep(4)
                placeholder.info("Hold...", icon="🧘")
                time.sleep(7)
                placeholder.info("Breathe out...", icon="😌")
                time.sleep(8)
            placeholder.success("Well done!")

    with st.expander(" grounding technique"):
        st.markdown("""
        **Use your senses to ground yourself.**
        Acknowledge:
        - **5** things you can see.
        - **4** things you can feel.
        - **3** things you can hear.
        - **2** things you can smell.
        - **1** thing you can taste.
        """)

    st.divider()
    st.header("🔗 Professional Help")
    st.markdown("""
    Aura is a companion, not a replacement for professional help. If you are in crisis, please reach out to these resources.
    - **988 Suicide & Crisis Lifeline** (US & Canada)
    - **111** (UK)
    - [**Find a Helpline**](https://findahelpline.com/) (International)
    """)

# --- Main Chat Interface ---
st.title("Aura - Your Mental Health Companion")
st.markdown(f"> *A gentle thought for you today: {get_random_thought()}*")
st.divider()

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "💖"):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How are you feeling today?"):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Get and display chatbot response
    with st.chat_message("assistant", avatar="💖"):
        message_placeholder = st.empty()
        with st.spinner("Aura is thinking..."):
            try:
                # Send the prompt to the generative model
                response = st.session_state.chat_session.send_message(prompt)
                full_response = response.text
                # Display the response with a typing effect
                message_placeholder.write_stream(stream_typing_effect(full_response))
                # Add chatbot response to session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except genai.types.StopCandidateException as e:
                st.warning("Aura stopped generating due to safety settings. Please rephrase your message.", icon="⚠️")
            except Exception as e:
                st.error(f"An error occurred: {e}", icon="🚨")
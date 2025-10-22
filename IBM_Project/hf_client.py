# hf_client.py

import streamlit as st
import requests

# --- Configuration ---
# Define the models we want to use from the Hugging Face Hub
EMOTION_API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
TTS_API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"

# --- API Call Helper ---
# A generic function to query the Hugging Face API
def query_hf_api(payload, api_url):
    """Sends a payload to a specified Hugging Face Inference API."""
    try:
        hf_token = st.secrets["HF_TOKEN"]
    except (KeyError, AttributeError):
        st.error("Hugging Face API token not found. Please add it to your secrets.", icon="🔒")
        return None

    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        st.toast(f"Hugging Face API Error: {response.json().get('error', 'Unknown error')}", icon="😥")
        return None
        
    return response

# --- Emotion Analysis Feature ---
@st.cache_data
def analyze_emotion(text_input):
    """
    Analyzes the emotion of a text using a Hugging Face model.
    Caches the result to avoid redundant API calls.
    """
    payload = {"inputs": text_input}
    response = query_hf_api(payload, EMOTION_API_URL)
    
    if response:
        try:
            # The API returns a list of lists of dictionaries
            # We want the label with the highest score
            emotions = response.json()[0]
            top_emotion = max(emotions, key=lambda x: x['score'])
            return top_emotion['label']
        except (IndexError, KeyError):
            return "unknown"
    return "unknown"

# --- Text-to-Speech Feature ---
@st.cache_data
def generate_speech(text_input):
    """
    Generates speech from text using a Hugging Face TTS model.
    Returns the audio content as bytes.
    """
    payload = {"inputs": text_input}
    response = query_hf_api(payload, TTS_API_URL)
    
    if response:
        return response.content
    return None
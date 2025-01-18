from openai import OpenAI
import streamlit as st
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")

# Initialize OpenAI client
client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

# Provider descriptions
PROVIDER_INFO = {
    "OpenAI": "Leading AI research company known for GPT models",
    "Anthropic": "Creator of Claude, focused on safe and ethical AI",
    "Google": "Tech giant offering Gemini and PaLM models",
    "Meta": "Creator of Llama, focusing on open-source AI",
    "Microsoft": "Tech leader with advanced language models",
    "Mistral": "Specializes in efficient, powerful language models",
    "Qwen": "Advanced multilingual AI models",
    "Development Agents": "Specialized agents for software development",
    "HelpingAI": "AI models focused on assistance and support",
    "Other": "Additional models from various providers"
}

# Load models from JSON data
with open('models.json') as f:
    MODELS = json.load(f)

# Unified model configuration
MODEL_CONFIG = {
    "temperature": {
        "Precise": 0.2,
        "Balanced": 0.5,
        "Creative": 0.8
    },
    "max_tokens": {
        "Short": 512,
        "Medium": 1024,
        "Long": 2048,
        "Extra Long": 4096
    },
    "top_p": 0.9,
    "presence_penalty": 0.1,
    "frequency_penalty": 0.1,
    "context_window": 8192  # Safe default for most models
}

def process_chat(message, selected_model, temperature, max_tokens):
    """Process chat messages with enhanced control over accuracy and length."""
    try:
        with st.spinner(""):
            # Create completion with the prepared messages
            stream = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "developer", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=MODEL_CONFIG["top_p"],
                presence_penalty=MODEL_CONFIG["presence_penalty"],
                frequency_penalty=MODEL_CONFIG["frequency_penalty"],
                stream=True
            )
            
            response_placeholder = st.empty()
            collected_messages = []
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    chunk_message = chunk.choices[0].delta.content
                    collected_messages.append(chunk_message)
                    response = "".join(collected_messages)
                    response_placeholder.markdown(f'<div class="chat-message">{response}</div>', unsafe_allow_html=True)
            
            return "".join(collected_messages)
            
    except Exception as e:
        error_msg = str(e)
        if "500" in error_msg:
            st.error("⚠️ Model unavailable. Please try another model.")
        elif "404" in error_msg:
            st.error(f"⚠️ Model '{selected_model}' not found.")
        elif "401" in error_msg:
            st.error("⚠️ Authentication failed.")
        else:
            st.error(f"⚠️ {error_msg}")
        return None

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #1E1E1E;
    }
    
    /* Hide elements */
    #MainMenu, footer, header {
        display: none !important;
    }
    
    /* Chat message */
    .chat-message {
        background-color: #2D2D2D;
        color: #FFFFFF;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        font-size: 1rem;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    
    /* Input container */
    .chat-input-container {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin-top: 1rem;
        background-color: #2D2D2D;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #3D3D3D;
    }
    
    /* Input field */
    .stTextInput > div > div {
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
        border: 1px solid #3D3D3D !important;
        border-radius: 0.5rem !important;
    }
    
    .stTextInput input {
        color: #FFFFFF !important;
        font-size: 1rem !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput input:focus {
        box-shadow: none !important;
        border-color: #4D4D4D !important;
    }
    
    .stTextInput input::placeholder {
        color: #808080 !important;
    }
    
    /* Send button */
    .send-button {
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
        border: 1px solid #3D3D3D !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        height: 46px !important;
        min-width: 80px !important;
    }
    
    .send-button:hover {
        background-color: #3D3D3D !important;
        border-color: #4D4D4D !important;
        transform: translateY(-1px);
    }
    
    .send-button:active {
        transform: translateY(0);
    }
    
    /* Select box */
    .stSelectbox > div {
        background-color: #2D2D2D !important;
    }
    
    .stSelectbox > div > div {
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
        border: 1px solid #3D3D3D !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem !important;
    }
    
    /* Container spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }
    
    /* Title */
    h1 {
        font-size: 1.75rem !important;
        margin-bottom: 2rem !important;
    }
    
    /* Provider info */
    .provider-info {
        background-color: #2D2D2D;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #CCCCCC;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1E1E1E;
    }
</style>
""", unsafe_allow_html=True)

# App layout
st.title("💭 Chat Bot")

# Model selection and settings in sidebar
with st.sidebar:
    st.markdown("### Model Selection")
    provider = st.selectbox("Select Provider", options=list(MODELS.keys()))
    st.markdown(f'<div class="provider-info">{PROVIDER_INFO[provider]}</div>', unsafe_allow_html=True)
    model = st.selectbox("Select Model", options=MODELS[provider])
    st.markdown(f"**Total Models:** {len(MODELS[provider])}")
    
    st.markdown("### Response Settings")
    
    # Accuracy control (temperature)
    accuracy_mode = st.select_slider(
        "Response Style",
        options=["Precise", "Balanced", "Creative"],
        value="Balanced",
        help="Adjust how creative or precise the responses should be"
    )
    temperature = MODEL_CONFIG["temperature"][accuracy_mode]
    
    # Max tokens control
    response_length = st.select_slider(
        "Response Length",
        options=["Short", "Medium", "Long", "Extra Long"],
        value="Medium",
        help="Control the maximum length of responses"
    )
    max_tokens = MODEL_CONFIG["max_tokens"][response_length]
    
    # Display current settings
    st.markdown("### Current Settings")
    st.markdown(f"""
    - Temperature: {temperature:.1f}
    - Max Tokens: {max_tokens:,}
    - Top P: {MODEL_CONFIG["top_p"]}
    - Presence Penalty: {MODEL_CONFIG["presence_penalty"]}
    - Frequency Penalty: {MODEL_CONFIG["frequency_penalty"]}
    """)

# Chat interface
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

# Create two columns for input and send button
col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input("", placeholder="Type your message here...", key="user_input", label_visibility="collapsed")

with col2:
    send_button = st.button("Send", key="send", help="Send message", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle input
if send_button or (user_input and user_input.strip() and "\n" in user_input):
    if user_input and user_input.strip():
        process_chat(user_input, model, temperature, max_tokens)

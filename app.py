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

# Process chat messages with enhanced control over accuracy and length.
def process_chat(message, selected_model, temperature, max_tokens):
    try:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": message})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(message)
        
        # Display assistant response with loading indicator
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Get response from API
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        # Display error message in red
        st.error(f"Error: {str(e)}")
        # Log the full error for debugging
        st.error("Please try again or select a different model.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        background-color: transparent;
        padding: 0;
        border-radius: 0;
        border: none;
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
st.sidebar.title("Model Settings")

# Provider selection
provider = st.sidebar.selectbox(
    "Select Provider",
    options=list(PROVIDER_INFO.keys()),
    format_func=lambda x: f"{x} - {PROVIDER_INFO[x]}"
)

# Model selection based on selected provider
if provider:
    model = st.sidebar.selectbox(
        "Select Model",
        options=MODELS.get(provider, []),
        key="model_select"
    )

    st.sidebar.markdown(f"**Total Models:** {len(MODELS.get(provider, []))}")

    # Response settings
    st.sidebar.markdown("### Response Settings")
    
    # Accuracy control (temperature)
    temperature = st.sidebar.slider(
        "Temperature (Creativity)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make the output more creative but less focused"
    )
    
    # Length control
    max_tokens = st.sidebar.slider(
        "Maximum Length",
        min_value=50,
        max_value=4000,
        value=2000,
        step=50,
        help="Maximum number of tokens in the response"
    )

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

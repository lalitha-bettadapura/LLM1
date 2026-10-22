import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables from a .env file (if present)
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="AI Chat",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Chat is ready to chat")
st.write("Ask any question and test me!")

# Load configuration from environment variables
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_CHOICE = os.getenv("MODEL", "gemini-3.5-flash-lite")

# Sidebar for optional overrides / status
st.sidebar.header("Configuration")
if API_KEY:
    st.sidebar.success("API Key loaded successfully!")
else:
    # Allow manual entry in sidebar if not found in environment or .env file
    API_KEY = st.sidebar.text_input(
        "Enter your Gemini API Key:",
        type="password",
        help="Get your key at https://aistudio.google.com/"
    )

st.sidebar.info(f"Using Model: **{MODEL_CHOICE}**")

# Initialize Chat History in Streamlit Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Form
if user_query := st.chat_input("Ask me anything..."):
    # Check if API Key is available
    if not API_KEY:
        st.error("Please set your `GOOGLE_API_KEY` in a `.env` file or enter it in the sidebar.")
    else:
        # 1. Display User Message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # 2. Call the Gemini API and Display Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*Thinking...*")
            
            try:
                # Initialize client with SSL verification disabled for corporate proxy/firewalls
                client = genai.Client(
                    api_key=API_KEY,
                    http_options=types.HttpOptions(client_args={"verify": False})
                )
                
                # Generate response using the configured model
                response = client.models.generate_content(
                    model=MODEL_CHOICE,
                    contents=user_query,
                )
                
                # Render answer
                message_placeholder.markdown(response.text)
                
                # Save assistant response to session state
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except APIError as e:
                message_placeholder.error(f"API Error: {e.message}")
            except Exception as e:
                message_placeholder.error(f"An unexpected error occurred: {e}")
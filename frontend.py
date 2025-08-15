# frontend.py
import streamlit as st
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64
from ai_agent import ask_ai, generate_image, generate_platform_content

# Configure page
st.set_page_config(
    page_title="Softvance AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #4f46e5;
        --secondary: #10b981;
        --accent: #f59e0b;
        --dark: #1e293b;
        --light: #f8fafc;
        --gray: #94a3b8;
    }
    
    .stApp {
        background-color: #f1f5f9;
    }
    
    .task-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: var(--gray);
        font-size: 0.9rem;
    }
    
    /* Better chat bubbles */
    .human-message {
        background-color: #4f46e5;
        color: white;
        border-radius: 18px 18px 0 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .ai-message {
        background-color: #f8fafc;
        color: #1e293b;
        border-radius: 18px 18px 18px 0;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-right: auto;
        border: 1px solid #e2e8f0;
    }
    
    .message-time {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 4px;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "task_type" not in st.session_state:
    st.session_state.task_type = "qa"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """You are a helpful AI assistant with access to web search.
Use the search tool for:
1. Current events (after 2023)
2. Fact verification
3. Breaking news
4. Recent scientific breakthroughs"""

# Header
st.title("🤖 Softvance AI Agent")
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <p style="color: var(--gray);">Multi-functional AI assistant for various tasks</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # API Key Management (optional - only if you want users to provide their own keys)
    # st.markdown("### 🔑 API Keys")
    # groq_key = st.text_input("GROQ API Key", type="password")
    # tavily_key = st.text_input("Tavily API Key", type="password")
    # stability_key = st.text_input("Stability API Key", type="password")
    
    st.markdown("### 📊 Usage Stats")
    st.metric("Current Task", st.session_state.task_type)
    st.metric("Messages", len(st.session_state.messages))
    
    if st.button("Clear Conversation", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Task Selection
with st.container():
    st.markdown("### 🛠️ Select Task Type")
    st.session_state.task_type = st.radio(
        "Task Type",
        ["qa", "image_generation", "platform_content"],
        horizontal=True,
        format_func=lambda x: {
            "qa": "Q&A",
            "image_generation": "Image Generation",
            "platform_content": "Platform Content"
        }[x]
    )

# Task Parameters
with st.container():
    st.markdown("### ⚙️ Task Parameters")
    
    if st.session_state.task_type == "qa":
        st.session_state.system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.system_prompt,
            height=150,
            help="Instructions for how the AI should behave"
        )
        
    elif st.session_state.task_type == "platform_content":
        st.session_state.platform = st.selectbox(
            "Platform",
            ["twitter", "facebook", "linkedin"],
            format_func=lambda x: x.capitalize(),
            help="Select the platform for content generation"
        )

# Input Area
input_col, button_col = st.columns([5, 1])
with input_col:
    user_input = st.text_input(
        "Enter your prompt...",
        placeholder="Type your message here...",
        label_visibility="collapsed"
    )

with button_col:
    send_button = st.button("Submit", use_container_width=True)

# Process Input
if send_button and user_input.strip():
    with st.spinner("Processing..."):
        try:
            if st.session_state.task_type == "qa":
                response = ask_ai(
                    question=user_input,
                    system_prompt=st.session_state.system_prompt,
                    chat_history=st.session_state.messages if st.session_state.messages else None
                )
                
                if response["status"] == "success":
                    timestamp = datetime.now().strftime("%H:%M")
                    st.session_state.messages.append({
                        "role": "human",
                        "content": user_input,
                        "time": timestamp
                    })
                    st.session_state.messages.append({
                        "role": "ai",
                        "content": response["output"],
                        "time": timestamp
                    })
                    
            elif st.session_state.task_type == "image_generation":
                response = generate_image(user_input)
                if response["status"] == "success":
                    st.session_state.last_image = response
                    
            elif st.session_state.task_type == "platform_content":
                response = generate_platform_content(
                    user_input,
                    st.session_state.platform
                )
                if response["status"] == "success":
                    st.session_state.last_content = response
            
            if response["status"] == "error":
                st.error(f"Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display Results
if st.session_state.task_type == "qa" and st.session_state.messages:
    st.markdown("### 💬 Conversation")
    for msg in st.session_state.messages:
        if msg["role"] == "human":
            st.markdown(f"""
            <div class="human-message">
                {msg["content"]}
                <div class="message-time">
                    {msg["time"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ai-message">
                {msg["content"]}
                <div class="message-time">
                    {msg["time"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.task_type == "image_generation" and hasattr(st.session_state, "last_image"):
    st.markdown("### 🖼️ Generated Image")
    image_data = base64.b64decode(st.session_state.last_image["image"])
    image = Image.open(BytesIO(image_data))
    st.image(image, caption=st.session_state.last_image["prompt"])
    
    # Download button
    buf = BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(
        label="Download Image",
        data=byte_im,
        file_name="generated_image.png",
        mime="image/png"
    )

elif st.session_state.task_type == "platform_content" and hasattr(st.session_state, "last_content"):
    st.markdown(f"### 📝 {st.session_state.platform.capitalize()} Content")
    st.markdown(st.session_state.last_content["content"])
    
    # Copy to clipboard button
    st.button(
        "Copy to Clipboard",
        on_click=lambda: st.session_state.last_content["content"],
        help="Content copied to clipboard!"
    )

# Footer
st.markdown("""
<div class="footer">
    <p>© 2023 Softvance AI | All Rights Reserved</p>
    <p>Powered by Groq, Stability AI, and Tavily</p>
</div>
""", unsafe_allow_html=True)
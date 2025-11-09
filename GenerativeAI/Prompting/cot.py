import streamlit as st
from google import genai
from dotenv import load_dotenv
import json
import os
import time

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client()

# System Prompt
SYSTEM_PROMPT = """
You are an expert AI assistant resolving user queries using a chain of thought.
You work in three phases: start, plan, and output.
You must plan first what needs to be done — the plan can have multiple steps.
Once enough planning is done, finally you give an output.

Rules:
1. Strictly follow the given JSON output format.
2. Only run one step at a time.
3. The sequence of steps is: Start → Plan (multiple times possible) → Output.

Output JSON Format:
{
    "step": "start" | "plan" | "output",
    "content": "string"
}
"""

# ------------------ Streamlit Page Config ------------------
st.set_page_config(page_title="AI Assistant", page_icon="🧠", layout="wide")

# ------------------ Custom CSS for Aesthetic UI ------------------
st.markdown("""
<style>
    body {background-color: #0e1117;}
    .stTextInput>div>div>input {
        border-radius: 10px;
        padding: 15px;
        font-size: 16px;
        border: 1px solid #555;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 16px !important;
    }
    .message-box {
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        font-weight: 500;
    }
    .start {background-color: #007bff;}
    .plan {background-color: #ffb300;}
    .output {background-color: #00c853;}
</style>
""", unsafe_allow_html=True)

# ------------------ Page Title ------------------
st.markdown("<h1 style='text-align:center; color:#00e5ff;'>🧠 Gemini Chain-of-Thought Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#b0bec5;'>Ask any question and watch the AI think step-by-step in real time!</p>", unsafe_allow_html=True)
st.markdown("---")

# ------------------ Chat History in Session State ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ Display previous chat ------------------
for message in st.session_state.messages:
    role, step, content = message
    if role == "user":
        st.markdown(f"<div class='message-box start'><b>🧑 You:</b> {content}</div>", unsafe_allow_html=True)
    else:
        css_class = step
        st.markdown(f"<div class='message-box {css_class}'><b>{'🤖 Gemini (' + step.upper() + '):'}</b> {content}</div>", unsafe_allow_html=True)

# ------------------ Input Box ------------------
prompt = st.text_input("💬 Type your question and press Enter:", key="user_input", placeholder="e.g. Solve (5+3)*2 or Explain gravity...", label_visibility="collapsed")

if prompt:
    # Display user message instantly
    st.session_state.messages.append(("user", "user", prompt))

    full_prompt = f"{SYSTEM_PROMPT}\nUser: {prompt}\nReply strictly in JSON as per rules."

    with st.spinner("🤔 Thinking..."):
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=full_prompt,
                    config={"response_mime_type": "application/json"}
                )
                break
            except Exception as e:
                st.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(5)
                else:
                    st.error("❌ Model unavailable. Try again later.")
                    st.stop()

        # Parse JSON
        raw_output = response.text.strip()
        try:
            parsed_result = json.loads(raw_output)
        except json.JSONDecodeError:
            st.error("⚠️ Invalid JSON output.")
            st.code(raw_output)
            st.stop()

        if isinstance(parsed_result, list):
            steps = parsed_result
        else:
            steps = [parsed_result]

        for step_data in steps:
            step = step_data.get("step", "").lower()
            content = step_data.get("content", "")
            if step in ["start", "plan", "output"]:
                st.session_state.messages.append(("assistant", step, content))
            else:
                st.session_state.messages.append(("assistant", "output", content))

    # Refresh page immediately to show the new messages
    st.rerun()

# ------------------ Footer ------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>✨ Designed by <b>Divyansh Singh</b> | Powered by <b>Gemini 2.5 Pro</b> ✨</p>", unsafe_allow_html=True)

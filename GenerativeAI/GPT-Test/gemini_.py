import streamlit as st
from dotenv import load_dotenv
from google import genai
import json
import time
import os

# --- Load Environment Variables ---
load_dotenv()

# --- Initialize Gemini Client ---
client = genai.Client()

# --- System Prompt ---
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

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Gemini Chain-of-Thought Assistant", page_icon="🧠", layout="centered")

st.title("🧠 Gemini Chain-of-Thought Assistant")
st.markdown("### Ask any question and watch how the AI thinks step-by-step.")

# --- User Input ---
user_query = st.text_input("💬 Ask something:")

if user_query:
    with st.spinner("Thinking... 🤔"):
        full_prompt = f"{SYSTEM_PROMPT}\nUser: {user_query}\nReply strictly in JSON as per the rules."

        # Retry mechanism
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
                    st.error("❌ Model is unavailable. Try again later.")
                    st.stop()

        # --- Parse Response ---
        raw_output = response.text.strip()
        try:
            parsed_result = json.loads(raw_output)
        except json.JSONDecodeError:
            st.error("⚠️ Model did not return valid JSON. Raw output:")
            st.code(raw_output)
            st.stop()

        # Ensure list
        if isinstance(parsed_result, list):
            steps = parsed_result
        else:
            steps = [parsed_result]

        # --- Display Each Step ---
        for step_data in steps:
            step = step_data.get("step", "").lower()
            content = step_data.get("content", "")

            if step == "start":
                st.info(f"🔥 **Start:** {content}")
            elif step == "plan":
                st.warning(f"🧠 **Plan:** {content}")
            elif step == "output":
                st.success(f"🤖 **Output:** {content}")
            else:
                st.text(f"⚠️ Unknown step type: {step}")

st.markdown("---")
st.caption("💡 Built with Google Gemini and Streamlit by Divyansh Singh 🚀")

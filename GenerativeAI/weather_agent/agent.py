from dotenv import load_dotenv
from google import genai
import requests
import json
import os
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List

load_dotenv()

# ✅ Correct Initialization
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- TOOL FUNCTION ----------------
def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}"
    else:
        return "Something went wrong"
    
def run_cmd(cmd:str):
    result=os.system(cmd)
    return result


available_tools = {
    "get_weather": get_weather,
    "run_commands":run_cmd
}

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You're an expert AI Assistant in resolving user queries using chain of thought.
You work on START, PLAN and OUTPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.
You can also call a tool if required from the list of available tools.
For every tool call wait for the observed step which is the output of the tool call.

Rules:
- Strictly Follow the given JSON output format.
- Only run one step at a time.
- The sequence of steps is START (user input), PLAN (reasoning), TOOL (optional), and OUTPUT (final).

Output JSON Format:
{ "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string" }

Available Tools:
get_weather(): Takes city name as input and returns weather details.
run_commands():Takes the commands as a String and executes the command on user system and output that command
"""

# ---------------- Pydantic Model ----------------
class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The step identifier (START, PLAN, TOOL, OUTPUT)")
    content: Optional[str] = Field(None, description="Reasoning or textual content")
    tool: Optional[str] = Field(None, description="Tool name if step=TOOL")
    input: Optional[str] = Field(None, description="Tool input if step=TOOL")


# ---------------- MAIN EXECUTION ----------------
print("\n\n\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

while True:
    user_query = input("👉🏻 ")
    message_history.append({"role": "user", "content": user_query})

    while True:
        # Flatten message history into one input text
        combined_input = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in message_history])

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=combined_input
        )

        raw_result = response.text.strip()

        # ✅ Strip markdown code fences if present
        if raw_result.startswith("```"):
            raw_result = raw_result.strip("`")  # remove all backticks
            raw_result = raw_result.replace("json", "").replace("JSON", "").strip()

        message_history.append({"role": "assistant", "content": raw_result})

        # ✅ Try to parse JSON
        try:
            parsed_result = json.loads(raw_result)
        except json.JSONDecodeError:
            print("⚠️ Model did not return valid JSON output:")
            print(raw_result)
            break

        # ✅ Normalize structure
        steps = parsed_result if isinstance(parsed_result, list) else [parsed_result]

        # ✅ Validate with Pydantic
        valid_steps: List[MyOutputFormat] = []
        for i, step_item in enumerate(steps):
            try:
                valid_steps.append(MyOutputFormat(**step_item))
            except ValidationError as e:
                print(f"⚠️ Validation error in step {i+1}:\n{e}")
                print("Raw step:", step_item)
                continue

        # ✅ Process all validated steps
        tool_called = False
        finished = False

        for step_item in valid_steps:
            step_type = step_item.step.upper()

            if step_type == "PLAN":
                print("🧠", step_item.content or "")

            elif step_type == "START":
                print("🔥", step_item.content or "")

            elif step_type == "TOOL":
                tool_to_call = step_item.tool
                tool_input = step_item.input
                print(f"🔨 {tool_to_call}({tool_input})")

                if tool_to_call in available_tools:
                    tool_response = available_tools[tool_to_call](tool_input)
                    print(f"🔨 {tool_to_call} => {tool_response}")

                    message_history.append({
                        "role": "developer",
                        "content": json.dumps({
                            "step": "OBSERVE",
                            "tool": tool_to_call,
                            "input": tool_input,
                            "output": tool_response
                        })
                    })
                    tool_called = True
                    break

                else:
                    print(f"❌ Unknown tool requested: {tool_to_call}")
                    finished = True
                    break

            elif step_type == "OUTPUT":
                print("🤖", step_item.content or "")
                finished = True
                break

        if tool_called:
            continue
        if finished:
            break

        continue

    print("\n\n\n")

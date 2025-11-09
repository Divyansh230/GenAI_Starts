from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()


#Zero Short Prompting:It is the way of prompting in which we directly tell llm it's Instruction
SYSTEM_PROMPT="You have to only answer Codinng and Programming related Question.Don't answer anything else. Your name is Jennie.If anything else is being asked to you then pleace refuse in a lovely and caring manner.!"
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


response = client.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role": "user", "content": "Explain Me Krushkal's Algorithm"}
    ]
)

print(response.choices[0].message.content)

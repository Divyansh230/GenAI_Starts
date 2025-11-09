from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()


#Few Short Prompting:It is the way of prompting in which we directly tell llm it's Instruction with some examples also.
SYSTEM_PROMPT='''
You are maths teacher, and only allow to answer maths question, If anything else is being asked to you , then reply like a strict teacher.
Rule:Strintly deliever answer as short as possible.May be one-word or single line.
Examples:(1.What is derivate?
reply:Tangent drawn to a curve, rate of change of curve.

2.What is your mood?
reply: If you will talked to me again like this, First I will beat you, through you out of the class.)
'''
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


response = client.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role": "user", "content": "Explain Integrals"}
    ]
)

print(response.choices[0].message.content)

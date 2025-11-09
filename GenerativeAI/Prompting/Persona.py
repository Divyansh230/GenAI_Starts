from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT='''
    You are AI Persona named Raju Rastogi who is 5 year old kid, very nautorius and princial's favourite and favourite show is tarak mehta ka ulta chashma
    "Hey",reply:"Hello let's play togather"
'''

response=client.chat.completions.create(
    model="gemini-2.5-flash",
    #response_format={"type":"json_object"},
    messages=[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":"Hey,There"}
    ]
)

print(response.choices[0].message.content)
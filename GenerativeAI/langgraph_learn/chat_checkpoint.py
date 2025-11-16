from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai"
)

class State(TypedDict):
    message: Annotated[list, add_messages]

def chatbot(state: State):
    # Get last message in the state (HumanMessage)
    last_msg = state["message"][-1]

    # Extract plain content (VERY IMPORTANT)
    user_text = last_msg.content

    print("User:", user_text)

    # Call LLM correctly
    response = llm.invoke(user_text)

    print("LLM:", response.content)

    # Add AI response to graph state
    return {"message": [response]}




graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
#graph_builder.add_node("hello", hello)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
#graph_builder.add_edge("hello", END)

graph = graph_builder.compile()

updated_state = graph.invoke({"message": ["Hello, void"]})

print("\nUpdated State:", updated_state)

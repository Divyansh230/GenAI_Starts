from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai"
)

# Define State
class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]


# Chatbot node
def chatbot(state: State):
    print("User:", state["user_query"])

    response = llm.invoke(state["user_query"])
    print("LLM:", response.content)

    state["llm_output"] = response.content
    return state


# Evaluator node (returns route)
def evaluat_response(state: State) -> Literal["gem_bot", "endnode"]:
    # Example: if LLM response contains "good", go to gem_bot
    if "good" in (state["llm_output"] or "").lower():
        return "gem_bot"
    else:
        return "endnode"


# Second LLM node
def gem_bot(state: State):
    print("\n--- In gem_bot Node ---")
    query = "Explain this in simple words: " + (state["llm_output"] or "")
    response = llm.invoke(query)

    state["llm_output"] = response.content
    return state


# End node
def endnode(state: State):
    print("\n--- End Node ---")
    return state


# Build graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("eval", evaluat_response)
graph_builder.add_node("gem_bot", gem_bot)
graph_builder.add_node("endnode", endnode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "eval")
graph_builder.add_conditional_edges("eval", evaluat_response)
graph_builder.add_edge("gem_bot", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

# Run
updated_state = graph.invoke({"user_query": "Hey, what is the mood?"})

print("\nFinal State:", updated_state)

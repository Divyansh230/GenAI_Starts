from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver

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

def compile_graphwithcheckpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)
   
       
DB_URI="mongodb://localhost:27017/langgraph"
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:

    graph_with_checkpoint=compile_graphwithcheckpointer(checkpointer=checkpointer)

    config={
        "configurable":{
            "thread_id":"Divyansh"
        }
    }

    updated_state = graph_with_checkpoint.invoke(State({"message": ["Hello, My name is Divyansh Singh"]}),config=config)

    print("\nUpdated State:", updated_state)


    #In my checkpointer one message will be under Divyans

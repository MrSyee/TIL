import os
from io import BytesIO
from typing import Annotated

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from PIL import Image
from typing_extensions import TypedDict

load_dotenv("../.env")


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


# Add a node
# Initialize the LLM and add it to the graph
llm = init_chat_model("openai:gpt-4.1")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)


# Add a entry point to the graph
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile()

# Visualize the graph
os.makedirs("output", exist_ok=True)
with open("output/graph.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())


# Run the chatbot
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break

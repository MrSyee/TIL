import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.graph.message import add_messages

load_dotenv("../.env")


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# Initialize the LLM and add it to the graph
llm = init_chat_model("openai:gpt-4.1")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

# Create a memory saver checkpoint
# in-memory checkpointer
memory = MemorySaver()

# Add a entry point to the graph
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=memory)

# Visualize the graph
os.makedirs("output", exist_ok=True)
with open("output/graph_memory.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())


# Interact with your chatbot
config = {"configurable": {"thread_id": "1"}}

user_input = "안녕. 내 이름은 말랑한거북이야."

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


# Ask a follow up question
user_input = "내 이름을 기억하니?"

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


# The only difference is we change the `thread_id` here to "2" instead of "1"
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    {"configurable": {"thread_id": "2"}},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


# Inspect the state
print("\n============Inspect the state============\n")
snapshot = graph.get_state(config)
print("Snapshot:", snapshot)

print("Snapshot next:", snapshot.next)

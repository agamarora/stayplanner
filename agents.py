from typing import Annotated
from typing_extensions import TypedDict
from os import getenv

from langgraph.graph import StateGraph,END
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langgraph.managed import IsLastStep

# ==== Environment Variables ====
GROQ_API_KEY = getenv("GROQ_API_KEY")

# ==== State Definition ====
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    agent_output: dict[str, str]
    name: str
    city: str
    hotel:str
    group: str
    interests:str
    num_people: int
    is_last_step: IsLastStep

# ==== Model Initialization ====
llm = ChatGroq(model="llama-3.3-70b-versatile")

# ==== Node Definition ====

def hotel_node(state: AgentState) -> Command:
    print("== Single Node ==")

    agent = create_react_agent(
        model=llm,
        tools=[],
        state_schema=AgentState,
        state_modifier=f"""
        Provide information about the guest, the city, group type, and the number of travelers.
        Guest Name: {state["name"]}
        City: {state["city"]}
        Group: {state["group"]}
        Number of People: {state["num_people"]}
        """,
    )

    result = agent.invoke(state, debug=True)
    print(f"{result=}")

    output = state["agent_output"]
    output["info"] = result["messages"][-1].content

    print(f"{state=}")

    return Command(
        update={
            "messages": [],
            "agent_output": output,
        },
    )

# ==== Define Workflow ====
def create_workflow():
    workflow = StateGraph(AgentState)

    # Add the hotel node
    workflow.add_node(hotel_node)

    # Set the entry point to the hotel node
    workflow.set_entry_point("hotel_node")

    return workflow.compile()

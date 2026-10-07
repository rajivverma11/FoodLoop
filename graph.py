from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import StackState

from agents.orchestrator import orchestrator
from agents.menuAgent import menu_agent
from agents.orderAgent import order_agent
from agents.synthesizer import synthesizer
from logger import setup_logger

logger = setup_logger(__name__)


# ---------------------------------------------------------
# Routing function
# ---------------------------------------------------------

def route_agents(state: StackState):

    route = state["route"]
    logger.info(f"Routing decision: {route}")

    if route == ["menu"]:
        return "menu"

    if route == ["order"]:
        return "order"

    if "menu" in route and "order" in route:
        return "both"

    logger.warning(
        f"Unknown route {route}. Defaulting to menu."
    )

    return "menu"


# ---------------------------------------------------------
# Both-agents node
# ---------------------------------------------------------

def both_agents(state: StackState):
    """
    Execute both specialist agents.

    Later this can be replaced with LangGraph Send()
    for parallel fan-out.
    """
    logger.info("Calling both agents")

    menu_result = menu_agent(state)
    order_result = order_agent(state)

    return {
        "menu_response": menu_result["menu_response"],
        "order_response": order_result["order_response"],
    }


# ---------------------------------------------------------
# Build graph
# ---------------------------------------------------------

builder = StateGraph(StackState)


# Add nodes
builder.add_node("orchestrator", orchestrator)
builder.add_node("menu", menu_agent)
builder.add_node("order", order_agent)
builder.add_node("both", both_agents)
builder.add_node("synthesizer", synthesizer)


# START -> Orchestrator
builder.add_edge(
    START,
    "orchestrator"
)


# Orchestrator -> appropriate specialist node
builder.add_conditional_edges(
    "orchestrator",
    route_agents,
    {
        "menu": "menu",
        "order": "order",
        "both": "both",
    }
)


# Specialist nodes -> Synthesizer
builder.add_edge("menu", "synthesizer")
builder.add_edge("order", "synthesizer")
builder.add_edge("both", "synthesizer")


# Synthesizer -> END
builder.add_edge(
    "synthesizer",
    END
)


# ---------------------------------------------------------
# Memory
# ---------------------------------------------------------

memory = MemorySaver()


# ---------------------------------------------------------
# Compile graph
# ---------------------------------------------------------

graph = builder.compile(
    checkpointer=memory
)
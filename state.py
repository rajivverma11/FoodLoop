
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
import operator


class StackState(TypedDict):

    messages: Annotated[list[AnyMessage], add_messages]
    user_query: str
    route: list[str]            #["menu_agent", "order_agent"]

    # Agent-local message buffers (isolated via add_messages reducer)
    menu_messages: Annotated[list[AnyMessage], add_messages]
    order_messages: Annotated[list[AnyMessage], add_messages]

    # Agent outputs
    menu_response: str
    order_response: str
    final_answer: str


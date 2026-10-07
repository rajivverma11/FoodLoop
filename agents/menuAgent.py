from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)

from config import llm
from state import StackState
from agents.prompts import MENU_AGENT_PROMPT
from tools.menuTools import search_menu_catalog
from logger import setup_logger

logger = setup_logger(__name__)

menu_tools = [search_menu_catalog]

llm_with_tools = llm.bind_tools(menu_tools)

tools_by_name = {
    tool.name: tool
    for tool in menu_tools
}


def menu_agent(state):
    """
    Menu Agent node.

    The LLM can call menu tools to search the FoodLoop menu.
    Tool results are sent back to the LLM until it produces
    a final response.
    """
    logger.info("Menu Agent started")

    messages = [
        SystemMessage(content=MENU_AGENT_PROMPT),
        *state["messages"],
    ]

    # Maximum of 5 tool-calling rounds
    for _ in range(5):

        response = llm_with_tools.invoke(messages)

        messages.append(response)

        # If LLM did not request any tools,
        # we have the final answer.
        if not response.tool_calls:
            logger.info("Menu Agent completed")
            return {
                "menu_response": response.content
            }

        # Execute each requested tool
        for tool_call in response.tool_calls:
            logger.info(
                f"Calling tool: {tool_call['name']} | "
                f"args={tool_call['args']}"
            )

            tool = tools_by_name[tool_call["name"]]
            tool_result = tool.invoke(tool_call["args"])

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    return {
        "menu_response": (
            "I'm sorry, I couldn't complete the menu search."
        )
    }










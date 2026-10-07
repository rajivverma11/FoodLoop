from langchain_core.messages import SystemMessage, ToolMessage

from config import llm
from agents.prompts import ORDER_AGENT_PROMPT
from tools.orderTools import lookup_order
from logger import setup_logger

logger = setup_logger(__name__)

# Tools available to the Order Agent
order_tools = [lookup_order]


# Give the LLM access to the tools
llm_with_tools = llm.bind_tools(order_tools)


# Easy lookup of tool name -> actual tool
tools_by_name = {
    tool.name: tool
    for tool in order_tools
}

def order_agent(state):
    """
    Order Agent.

    Handles order tracking and status questions
    using the lookup_order tool.
    """
    logger.info("Order Agent started")

    messages = [
        SystemMessage(content=ORDER_AGENT_PROMPT),
        *state["messages"],
    ]

    # Allow maximum 5 tool-calling rounds
    for _ in range(5):

        # Ask LLM what to do
        response = llm_with_tools.invoke(messages)

        # Keep the LLM response in local conversation history
        messages.append(response)

        # If there are no tool calls, this is the final answer
        if not response.tool_calls:
            logger.info("Order Agent completed")
            return {
                "order_response": response.content
            }

        # Execute tools requested by the LLM
        for tool_call in response.tool_calls:
            logger.info(
                        f"Calling tool: {tool_call['name']} | "
                        f"args={tool_call['args']}"
                    )

            tool = tools_by_name[tool_call["name"]]            

            tool_result = tool.invoke(
                tool_call["args"]
            )

            # Give tool result back to the LLM
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    return {
        "order_response":
            "I'm sorry, I couldn't complete the order lookup."
    }
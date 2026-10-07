from langchain_core.messages import SystemMessage, HumanMessage

from config import llm
from agents.prompts import SYNTHESIZER_PROMPT

from logger import setup_logger

logger = setup_logger(__name__)

def synthesizer(state):
    """
    Combines responses from Menu Agent and Order Agent
    into one final response.
    """
    logger.info("Synthesizer started")
    
    menu_response = state.get("menu_response", "")
    order_response = state.get("order_response", "")

    # If only Menu Agent responded, no need for another LLM call
    if menu_response and not order_response:
        return {
            "final_answer": menu_response
        }

    # If only Order Agent responded, no need for another LLM call
    if order_response and not menu_response:
        return {
            "final_answer": order_response
        }

    # If neither agent produced a response
    if not menu_response and not order_response:
        return {
            "final_answer": "I'm sorry, I couldn't process your request."
        }

    # Both agents responded — ask LLM to combine them
    combined_response = f"""
    Menu Agent Response:
    {menu_response}

    Order Agent Response:
    {order_response}
    """

    response = llm.invoke(
        [
            SystemMessage(content=SYNTHESIZER_PROMPT),
            HumanMessage(content=combined_response),
        ]
    )

    return {
        "final_answer": response.content
    }
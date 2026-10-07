from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from config import llm
from agents.prompts import ORCHESTRATOR_PROMPT

from logger import setup_logger

logger = setup_logger(__name__)


class RouteDecision(BaseModel):
    agents: list[Literal["menu", "order"]] = Field(
        description="Specialist agents that should handle the request."
    )


orchestrator_llm = llm.with_structured_output(RouteDecision)


def orchestrator(state):

    user_query = state["user_query"]
    logger.info(f"Received query: {user_query}")

    response = orchestrator_llm.invoke(
        [
            SystemMessage(content=ORCHESTRATOR_PROMPT),
            HumanMessage(content=user_query),
        ]
    )
    logger.info(f"Routing to: {response.agents}")

    return {
        "route": response.agents
    }
from typing import Any

from multi_agents.graph import Node
from rich.console import Console

from noir.multi_agent.schema import StateSchema
from noir.llm_agents import LedMatrixAssistant, LedMatrixAssistantDeps

from .utils import get_mongodb_history


console = Console()


async def run(state: StateSchema) -> dict[str, Any]:
    console.log("running noir...")

    noir = LedMatrixAssistant(mongodb_message_history=get_mongodb_history())
    noir_output = await noir.generate(
        user_prompt=f"Message: {state.message}",
        agent_deps=LedMatrixAssistantDeps(
            matrix_size=state.matrix_size,
        ),
    )

    return {
        "explanation": noir_output.explanation,
    }


noir = Node(
    name="noir",
    run=run,
)

from typing import Any

from multi_agents.graph import Node
from rich.console import Console

from noire.llm_agents import LedMatrixAssistant, LedMatrixAssistantDeps
from noire.multi_agent.schema import StateSchema


console = Console()


async def run(state: StateSchema) -> dict[str, Any]:
    console.log("running noir...")

    noir = LedMatrixAssistant()
    noir_output = await noir.generate(
        user_prompt=f"Message: {state.message}",
        agent_deps=LedMatrixAssistantDeps(
            matrix_size=state.matrix_size,
        ),
    )

    return {
        "answer": noir_output.answer,
        "displayed_image": noir_output.displayed_image,
    }


noir = Node(
    name="noir",
    run=run,
)

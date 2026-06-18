from typing import Any

from multi_agents.graph import Node
from rich.console import Console

from noir.config import config
from noir.display.ascii_art import matrix_to_ascii_art
from noir.multi_agent.schema import StateSchema
from noir.llm_agents import LedMatrixAssistant, LedMatrixAssistantDeps


console = Console()


async def run(state: StateSchema) -> dict[str, Any]:
    console.log("running noir...")

    noir = LedMatrixAssistant()
    noir_output = await noir.generate(
        user_prompt=f"Message: {state.message}",
        agent_deps=LedMatrixAssistantDeps(
            matrix_size=config.pixoo_matrix_size,
            relevant_memories=state.relevant_memories,
        ),
    )

    return {
        "explanation": noir_output.explanation,
        "images": noir_output.images,
        "images_ascii": "\n\n".join(
            matrix_to_ascii_art(image) for image in noir_output.images
        ),
        "brightness": noir_output.brightness,
        "velocity": noir_output.velocity,
        "repetitions": noir_output.repetitions,
    }


noir = Node(
    name="noir",
    run=run,
)

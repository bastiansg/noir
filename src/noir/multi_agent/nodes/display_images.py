from typing import Any
from rich.console import Console

from multi_agents.graph import Node

from noir.display.led_matrix import display_led_matrix_image
from noir.multi_agent.schema import StateSchema


console = Console()


async def run(state: StateSchema) -> dict[str, Any]:
    console.log("running noir...")

    brightness = state.brightness
    assert brightness is not None

    velocity = state.velocity
    assert velocity is not None

    repetitions = state.repetitions
    assert repetitions is not None

    await display_led_matrix_image(
        images=state.images,
        brightness=brightness,
        velocity=velocity,
        repetitions=repetitions,
    )

    return {}


display_images = Node(
    name="display_images",
    run=run,
)

from pathlib import Path
from llm_agents.meta.interfaces import LLMAgent

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    StrictInt,
    StrictStr,
)

from pydantic_ai import Agent, ToolOutput, RunContext
from noir.display.led_matrix import LedMatrixImage, LedMatrixVelocity


class LedMatrixAssistantDeps(BaseModel):
    matrix_size: PositiveInt = Field(
        description="Width and height of the square LED matrix.",
    )

    relevant_memories: StrictStr = Field(
        description="Relevant memories about communicating with the user.",
    )


class LedMatrixAssistantOutput(BaseModel):
    explanation: StrictStr = Field(
        description=(
            "Explanation of what the LED matrix image was intended to communicate."
        ),
        min_length=1,
    )

    images: list[LedMatrixImage] = Field(
        min_length=2,
        max_length=10,
        description=(
            "Sequence of LED matrix images forming the complete public response."
        ),
    )

    brightness: StrictInt = Field(
        ge=25,
        le=100,
        description="Display brightness from 25 to 100.",
    )

    velocity: LedMatrixVelocity = Field(
        description="Animation velocity: slow, medium, or fast.",
    )

    repetitions: StrictInt = Field(
        ge=1,
        le=5,
        description="Number of times to loop the full image sequence.",
    )


agent = Agent(  # type: ignore
    name="led-matrix-assistant",
    model="gpt-5.4-2026-03-05",
    deps_type=LedMatrixAssistantDeps,
    output_type=ToolOutput(LedMatrixAssistantOutput),
    retries=3,
)


@agent.system_prompt
async def get_system_prompt(ctx: RunContext[LedMatrixAssistantDeps]) -> str:
    return LLMAgent.read_file(
        file_path=str(Path(__file__).with_name("system-prompt.md"))
    ).format(**ctx.deps.model_dump())


class LedMatrixAssistant(
    LLMAgent[LedMatrixAssistantDeps, LedMatrixAssistantOutput]
):
    def __init__(
        self,
        max_concurrency: int = 10,
    ):
        super().__init__(agent=agent, max_concurrency=max_concurrency)

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


class NoirDeps(BaseModel):
    matrix_size: PositiveInt = Field(
        description="Width and height of the square LED matrix.",
    )

    relevant_memories: StrictStr = Field(
        description="Relevant memories about communicating with the user.",
    )


class NoirOutput(BaseModel):
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
        description="Animation velocity: super-fast, fast, medium, or slow.",
    )

    repetitions: StrictInt = Field(
        ge=1,
        le=5,
        description="Number of times to loop the full image sequence.",
    )


agent = Agent(  # type: ignore
    name="noir",
    model="gpt-5.4-2026-03-05",
    deps_type=NoirDeps,
    output_type=ToolOutput(NoirOutput),
    retries=3,
)


@agent.system_prompt
async def get_system_prompt(ctx: RunContext[NoirDeps]) -> str:
    return LLMAgent.read_file(
        file_path=str(Path(__file__).with_name("system-prompt.md"))
    ).format(**ctx.deps.model_dump())


class Noir(LLMAgent[NoirDeps, NoirOutput]):
    def __init__(
        self,
        max_concurrency: int = 10,
    ):
        super().__init__(agent=agent, max_concurrency=max_concurrency)

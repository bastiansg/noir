from pathlib import Path

from llm_agents.meta.interfaces import LLMAgent
from pydantic import BaseModel, Field, PositiveInt, StrictStr
from pydantic_ai import Agent, RunContext, ToolOutput

from noir.llm_agents.tools import display_led_matrix_image_tool


class LedMatrixAssistantDeps(BaseModel):
    matrix_size: PositiveInt = Field(
        default=8,
        description="Width and height of the square LED matrix.",
    )


class LedMatrixAssistantOutput(BaseModel):
    explanation: StrictStr = Field(
        description="Explanation of what the LED matrix image was intended to communicate.",
        min_length=1,
    )


def _read_system_prompt() -> str:
    return LLMAgent.read_file(
        file_path=str(Path(__file__).with_name("system-prompt.md"))
    )


agent = Agent(  # type: ignore
    name="led-matrix-assistant",
    model="gpt-5.4-2026-03-05",
    system_prompt=_read_system_prompt(),
    deps_type=LedMatrixAssistantDeps,
    output_type=ToolOutput(LedMatrixAssistantOutput),
    retries=3,
    tools=[display_led_matrix_image_tool],
)


@agent.system_prompt
async def get_system_prompt(ctx: RunContext[LedMatrixAssistantDeps]) -> str:
    return _read_system_prompt().format(**ctx.deps.model_dump())


class LedMatrixAssistant(
    LLMAgent[LedMatrixAssistantDeps, LedMatrixAssistantOutput]
):
    def __init__(self, max_concurrency: int = 10):
        super().__init__(agent=agent, max_concurrency=max_concurrency)

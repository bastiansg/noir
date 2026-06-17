from pathlib import Path

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from pydantic import BaseModel, Field, PositiveInt, StrictStr

from pydantic_ai import Agent, RunContext, NativeOutput
from pydantic_ai.capabilities import ReinjectSystemPrompt

from noir.llm_agents.tools import display_led_matrix_image_tool
from noir.llm_agents.utils import hide_tools_after_limit, tool_logging_handler


class LedMatrixAssistantDeps(BaseModel):
    matrix_size: PositiveInt = Field(
        description="Width and height of the square LED matrix.",
    )


class LedMatrixAssistantOutput(BaseModel):
    explanation: StrictStr = Field(
        description="Explanation of what the LED matrix image was intended to communicate.",
        min_length=1,
    )


agent = Agent(  # type: ignore
    name="led-matrix-assistant",
    model="gpt-5.4-2026-03-05",
    deps_type=LedMatrixAssistantDeps,
    output_type=NativeOutput(LedMatrixAssistantOutput),
    retries=3,
    tools=[display_led_matrix_image_tool],
    prepare_tools=hide_tools_after_limit,  # type: ignore
    event_stream_handler=tool_logging_handler,  # type: ignore
    capabilities=[ReinjectSystemPrompt()],
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
        mongodb_message_history: MongoDBMessageHistory,
        max_concurrency: int = 10,
    ):
        super().__init__(
            agent=agent,
            max_concurrency=max_concurrency,
            mongodb_message_history=mongodb_message_history,
        )

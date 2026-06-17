import json

from typing import Any, AsyncIterator

from pydantic_ai.messages import AgentStreamEvent
from pydantic_ai import RunContext, FunctionToolCallEvent, ToolDefinition

from rich.console import Console


console = Console()


TOOL_CALL_LIMIT = 5


async def hide_tools_after_limit(
    ctx: RunContext,
    tool_defs: list[ToolDefinition],
) -> list[ToolDefinition] | None:
    if ctx.usage.tool_calls >= TOOL_CALL_LIMIT:
        console.log(f"tool call limit reached: {TOOL_CALL_LIMIT}")
        return None

    return tool_defs


async def tool_logging_handler(
    run_context: RunContext[Any],
    stream: AsyncIterator[AgentStreamEvent],
) -> None:
    async for event in stream:
        if isinstance(event, FunctionToolCallEvent):
            console.log(
                {
                    "tool": event.part.tool_name,
                    "args": json.loads(event.part.args),  # type: ignore
                }
            )

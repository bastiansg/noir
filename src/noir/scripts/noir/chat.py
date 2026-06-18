import json
import uuid
import logfire
import asyncio

from time import sleep

from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console
from rich.pretty import pprint

from noir.config import config
from noir.display.ascii_art import matrix_to_ascii_art
from noir.memory import get_memory
from noir.multi_agent import get_multi_agent, get_multi_agent_context


EXIT_COMMANDS = {"exit", "quit", "q"}
NOIR_BANNER = (
    "███╗   ██╗ ██████╗ ██╗██████╗ ",
    "████╗  ██║██╔═══██╗██║██╔══██╗",
    "██╔██╗ ██║██║   ██║██║██████╔╝",
    "██║╚██╗██║██║   ██║██║██╔══██╗",
    "██║ ╚████║╚██████╔╝██║██║  ██║",
    "╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═╝",
)

MEMORY_PROMPT = """
Extract only durable memories about which LED-matrix images, abstract patterns, and
visual styles communicated a message well or poorly to this user. Each memory must
identify the relevant visual characteristic, the intended message, and whether it
helped or hindered understanding. Do not store preferences or facts unrelated to the
visual content of the images. Do not treat N.O.I.R.'s private explanation as understood
unless the user confirms it. Exclude transient details and unsupported interpretations.
Preserve the rule that images cannot contain text, letters, numbers, emoji, icons,
known symbols, or real writing systems.
""".strip()


console = Console()


logfire.configure(service_name="noir")
_ = logfire.instrument_pydantic_ai()
sleep(1)


def render_header() -> None:
    banner = Text(justify="center")
    styles = ("bold bright_cyan", "bold cyan", "bold bright_magenta")
    for line, style in zip(NOIR_BANNER, styles * 2, strict=True):
        banner.append(f"{line}\n", style=style)

    banner.append(
        "N O I S E   O F   I N C O N S I S T E N T   R O B O T",
        style="dim bright_cyan",
    )
    console.print(Align.center(banner))


def format_relevant_memory(result: dict) -> str:
    metadata = result.get("metadata")
    if metadata is None:
        return f"- {result['memory']}"

    return (
        f"- {result['memory']}\n"
        f"  Source: {json.dumps(metadata, separators=(',', ':'))}"
    )


async def run_chat() -> None:
    multi_agent = get_multi_agent()
    context = get_multi_agent_context()

    render_header()
    console.print("[dim]Type 'exit', 'quit', or 'q' to leave.[/dim]\n")

    state = None
    session_id = config.session_id
    memory = get_memory()

    while True:
        message = Prompt.ask("[bold cyan]you[/bold cyan]").strip()

        if message.lower() in EXIT_COMMANDS:
            break

        if not message:
            continue

        if state is not None:
            console.log("creating memories...")
            await asyncio.to_thread(
                memory.add,
                [
                    {
                        "role": "assistant",
                        "content": state.model_dump_json(
                            include={
                                "explanation",
                                "images_ascii",
                            },
                        ),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                user_id=session_id,
                prompt=MEMORY_PROMPT,
                # metadata={
                #     "explanation": state.explanation,
                #     "images_ascii": state.images_ascii,
                #     "brightness": state.brightness,
                #     "velocity": state.velocity,
                #     "repetitions": state.repetitions,
                # },
            )

        with console.status("[cyan]NOIR is thinking...[/cyan]"):
            memory_results = await asyncio.to_thread(
                memory.search,
                query=message,
                filters={"user_id": session_id},
                top_k=5,
                threshold=0.3,
            )

            relevant_memories = "\n".join(
                format_relevant_memory(result)
                for result in memory_results["results"]
            )

            state = await multi_agent.run(
                input_state={
                    "message": message,
                    "relevant_memories": relevant_memories,
                },
                context=context,
                thread_id=uuid.uuid4().hex,
            )

        assert state is not None
        pprint(
            state.model_dump(
                include={
                    "message",
                    "explanation",
                    "relevant_memories",
                    "brightness",
                    "velocity",
                    "repetitions",
                }
            )
        )

        for frame, image in enumerate(state.images, start=1):
            console.print(
                Align.left(
                    Panel.fit(
                        Text(
                            matrix_to_ascii_art(image),
                            style=f"bold {image.color}",
                            overflow="ignore",
                            no_wrap=True,
                        ),
                        title=f"[bold]LED Matrix · Frame {frame}[/bold]",
                        border_style=image.color,
                        padding=(1, 2),
                    )
                )
            )


if __name__ == "__main__":
    asyncio.run(run_chat())

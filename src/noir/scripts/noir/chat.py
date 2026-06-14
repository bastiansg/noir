import uuid
import asyncio

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from noir.multi_agent import get_multi_agent, get_multi_agent_context


EXIT_COMMANDS = {"exit", "quit", "q"}


console = Console()


def render_header() -> None:
    title = Text("N.O.I.R.", style="bold white")
    subtitle = Text("Noise of Inconsistent Robot", style="dim cyan")

    console.print(
        Panel(
            Align.center(Text.assemble(title, "\n", subtitle)),
            border_style="cyan",
        )
    )


async def run_chat() -> None:
    multi_agent = get_multi_agent()
    context = get_multi_agent_context()

    render_header()
    console.print("[dim]Type 'exit', 'quit', or 'q' to leave.[/dim]\n")

    while True:
        message = Prompt.ask("[bold cyan]you[/bold cyan]").strip()

        if message.lower() in EXIT_COMMANDS:
            break

        if not message:
            continue

        with console.status("[cyan]NOIR is thinking...[/cyan]"):
            state = await multi_agent.run(
                input_state={
                    "message": message,
                    "matrix_size": context.matrix_size,
                },
                context=context,
                thread_id=uuid.uuid4().hex,
            )

        console.print(
            Panel(
                state.answer,
                title="NOIR",
                border_style="magenta",
            )
        )
        console.print(
            Panel(
                state.displayed_image,
                title="LED Matrix",
                border_style="green",
            )
        )


if __name__ == "__main__":
    asyncio.run(run_chat())

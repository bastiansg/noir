import time

from rich.panel import Panel
from rich.console import Console

from serial import SerialException
from subprocess import CalledProcessError

from noir.display.pixoo import PixooConnection
from noir.scripts.pixoo.images import dsp_images


console = Console()


def _color_to_rgb(color):
    return color["r"], color["g"], color["b"]


def _to_rgb_matrix(dsp_image):
    primary_color = _color_to_rgb(dsp_image["primary_color"])
    background_color = _color_to_rgb(dsp_image["background_color"])
    pixels = dsp_image["image"]

    return [
        [
            primary_color if value else background_color
            for value in pixels[index : index + 16]
        ]
        for index in range(0, len(pixels), 16)
    ]


def main() -> None:
    try:
        with PixooConnection() as pixoo:
            for index, dsp_image in enumerate(
                dsp_images,
                start=1,
            ):
                pixoo.send_rgb_matrix(_to_rgb_matrix(dsp_image))
                console.print(
                    Panel(
                        f"sent {dsp_image['name']} ({index}/{len(dsp_images)})",
                        title="Pixoo Space Invaders",
                        border_style="green",
                    )
                )

                time.sleep(1)

    except (CalledProcessError, SerialException, FileNotFoundError) as exc:
        console.print(
            Panel(
                str(exc),
                title="Pixoo failed",
                border_style="red",
            )
        )

        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

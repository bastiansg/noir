import time

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from noir.config import config
from noir.display.pixoo import RGB, PixooDisplay, RGBMatrix


LedMatrixColor = Literal["white", "cyan", "yellow", "magenta", "red"]
LedMatrixVelocity = Literal["slow", "medium", "fast"]
LedMatrixPixel = Annotated[int, Field(ge=0, le=1)]

BACKGROUND_COLOR = RGB(red=0, green=0, blue=0)
LED_MATRIX_COLORS: dict[LedMatrixColor, RGB] = {
    "white": RGB(red=255, green=255, blue=255),
    "cyan": RGB(red=0, green=255, blue=255),
    "yellow": RGB(red=255, green=255, blue=0),
    "magenta": RGB(red=255, green=0, blue=255),
    "red": RGB(red=255, green=0, blue=0),
}
LED_MATRIX_SLEEP_SECONDS: dict[LedMatrixVelocity, float] = {
    "slow": 0.8,
    "medium": 0.5,
    "fast": 0.2,
}


class LedMatrixImage(BaseModel):
    model_config = ConfigDict(frozen=True)
    color: LedMatrixColor = Field(
        description=(
            "Foreground color for active pixels: white for neutral, clear, or direct "
            "communication; cyan for calm, trust, or reassurance; yellow for attention, "
            "curiosity, joy, or uncertainty; magenta for excitement, affection, or "
            "intensity; red for danger, refusal, anger, strong warning, or urgent alarm."
        ),
    )

    pixels: list[list[LedMatrixPixel]] = Field(
        description=(
            f"{config.pixoo_matrix_size}x{config.pixoo_matrix_size} binary mask. Use 1 "
            "for active foreground pixels and 0 for inactive background pixels. Include "
            "at least one active pixel. Use abstract symbolic pixel language, motion, "
            "rhythm, color, and shape only. Do not display text, letters, numbers, words, "
            "initials, punctuation, or emoji-like glyphs. Prefer bold, high-contrast "
            "pixel art that remains readable on a small LED matrix."
        ),
    )

    @field_validator("pixels")
    @classmethod
    def validate_dimensions(
        cls,
        pixels: list[list[LedMatrixPixel]],
    ) -> list[list[LedMatrixPixel]]:
        size = config.pixoo_matrix_size
        if len(pixels) != size or any(len(row) != size for row in pixels):
            raise ValueError(f"Expected {size}x{size} image.")

        if not any(pixel for row in pixels for pixel in row):
            raise ValueError("Expected at least one active pixel.")

        return pixels


@lru_cache()
def get_display() -> PixooDisplay:
    display = PixooDisplay()
    display.connect()
    display.send_rgb_matrix(_black_rgb_matrix())

    return display


async def display_led_matrix_image(
    images: Annotated[
        list[LedMatrixImage],
        Field(
            min_length=2,
            max_length=10,
            description=(
                "Sequence of 2 to 10 LED matrix images to display as the complete public "
                "response. Keep each frame simple enough to work on the configured square "
                "LED matrix."
            ),
        ),
    ],
    brightness: Annotated[
        int,
        Field(
            ge=25,
            le=100,
            description=(
                "Display brightness from 25 to 100. Choose enough contrast for the image "
                "to be readable on the LED matrix."
            ),
        ),
    ],
    velocity: Annotated[
        LedMatrixVelocity,
        Field(
            description=(
                "Animation velocity. Use slow for calm or reassurance, fast for "
                "excitement or urgency, and medium for doubt, hesitation, or confusion."
            ),
        ),
    ],
    repetitions: Annotated[
        int,
        Field(
            ge=1,
            le=5,
            description=(
                "Required number of times to loop the full image sequence. Use fewer "
                "repetitions for calm or reassurance and more repetitions for excitement "
                "or urgency."
            ),
        ),
    ],
) -> None:
    """Display an abstract animated response on the LED matrix.

    Args:
        images: Sequence of 2 to 10 abstract LED matrix images.
        brightness: Display brightness from 25 to 100.
        velocity: Animation velocity: slow, medium, or fast.
        repetitions: Required number of times to loop the full image sequence.
    """

    display = get_display()
    display.set_brightness(brightness)
    sleep_seconds = LED_MATRIX_SLEEP_SECONDS[velocity]
    for _ in range(repetitions):
        for image in images:
            display.send_rgb_matrix(_to_rgb_matrix(image))
            time.sleep(sleep_seconds)

    display.send_rgb_matrix(_black_rgb_matrix())


def _to_rgb_matrix(image: LedMatrixImage) -> RGBMatrix:
    foreground_color = LED_MATRIX_COLORS[image.color]

    return RGBMatrix(
        pixels=[
            [foreground_color if pixel else BACKGROUND_COLOR for pixel in row]
            for row in image.pixels
        ]
    )


def _black_rgb_matrix() -> RGBMatrix:
    return RGBMatrix(
        pixels=[
            [BACKGROUND_COLOR for _ in range(config.pixoo_matrix_size)]
            for _ in range(config.pixoo_matrix_size)
        ]
    )

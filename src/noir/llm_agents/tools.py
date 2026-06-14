import time

from functools import lru_cache
from typing import Annotated, Literal

from pydantic_ai import Tool
from pydantic import BaseModel, ConfigDict, Field, field_validator

from noir.config import config
from noir.display.pixoo import RGB, RGBMatrix, PixooDisplay


LedMatrixColor = Literal["white", "cyan", "yellow", "magenta"]
LedMatrixPixel = Annotated[int, Field(ge=0, le=1)]

BACKGROUND_COLOR = RGB(red=0, green=0, blue=0)
LED_MATRIX_COLORS: dict[LedMatrixColor, RGB] = {
    "white": RGB(red=255, green=255, blue=255),
    "cyan": RGB(red=0, green=255, blue=255),
    "yellow": RGB(red=255, green=255, blue=0),
    "magenta": RGB(red=255, green=0, blue=255),
}


class LedMatrixImage(BaseModel):
    model_config = ConfigDict(frozen=True)
    color: LedMatrixColor = Field(
        description="Foreground color for active pixels.",
    )

    pixels: list[list[LedMatrixPixel]] = Field(
        description="16x16 binary mask. Use 1 for active pixels and 0 for off pixels.",
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

    return display


async def display_led_matrix_image(
    images: Annotated[
        list[LedMatrixImage],
        Field(
            min_length=1,
            max_length=5,
            description="Sequence of 1 to 5 LED matrix images to display.",
        ),
    ],
    brightness: Annotated[
        int,
        Field(
            ge=25,
            le=100,
            description="Display brightness from 25 to 100.",
        ),
    ],
    sleep_seconds: Annotated[
        float,
        Field(
            ge=0.5,
            le=2.0,
            description="Seconds to wait between images.",
        ),
    ],
) -> None:
    """Display a sequence of images in the LED matrix.

    Args:
        images: Sequence of 1 to 5 LED matrix images.
        brightness: Display brightness from 25 to 100.
        sleep_seconds: Seconds to wait between images.
    """

    display = get_display()
    for image in images:
        display.send_rgb_matrix(_to_rgb_matrix(image))
        display.set_brightness(brightness)
        time.sleep(sleep_seconds)


def _to_rgb_matrix(image: LedMatrixImage) -> RGBMatrix:
    foreground_color = LED_MATRIX_COLORS[image.color]

    return RGBMatrix(
        pixels=[
            [foreground_color if pixel else BACKGROUND_COLOR for pixel in row]
            for row in image.pixels
        ]
    )


display_led_matrix_image_tool = Tool(
    function=display_led_matrix_image,
    description="Display 1 to 5 colored 16x16 images in the LED matrix.",
    docstring_format="google",
    require_parameter_descriptions=True,
)

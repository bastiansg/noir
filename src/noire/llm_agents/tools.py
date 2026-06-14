import json
import os
import re

from itertools import chain
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt, StrictStr
from pydantic_ai import Tool


DEFAULT_LED_MATRIX_OUTPUT_PATH = "/tmp/noire-led-matrix.json"
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


class LedMatrixDisplayResult(BaseModel):
    matrix_size: PositiveInt
    image_path: StrictStr
    description: StrictStr


def _validate_pixels(matrix_size: int, pixels: list[list[str]]) -> None:
    if len(pixels) != matrix_size:
        raise ValueError(
            f"Expected {matrix_size} rows, received {len(pixels)}."
        )

    invalid_rows = [
        row_index
        for row_index, row in enumerate(pixels)
        if len(row) != matrix_size
    ]

    if invalid_rows:
        raise ValueError(
            f"Rows must contain {matrix_size} colors: {invalid_rows}."
        )

    invalid_colors = [
        color
        for color in chain.from_iterable(pixels)
        if HEX_COLOR_PATTERN.fullmatch(color) is None
    ]

    if invalid_colors:
        raise ValueError(f"Invalid RGB hex colors: {invalid_colors}.")


async def display_led_matrix_image(
    matrix_size: Annotated[
        PositiveInt,
        Field(description="Width and height of the square LED matrix."),
    ],
    pixels: Annotated[
        list[list[str]],
        Field(
            description=(
                "Square image as rows of RGB hex colors. The outer list length "
                "and each row length must match matrix_size."
            )
        ),
    ],
    description: Annotated[
        StrictStr,
        Field(description="Short description of the image being displayed."),
    ],
) -> LedMatrixDisplayResult:
    """Display an image in the LED matrix.

    Args:
        matrix_size: Width and height of the square LED matrix.
        pixels: Square image as rows of RGB hex colors.
        description: Short description of the image being displayed.
    """

    _validate_pixels(matrix_size=matrix_size, pixels=pixels)

    image_path = os.getenv(
        "NOIRE_LED_MATRIX_OUTPUT_PATH",
        DEFAULT_LED_MATRIX_OUTPUT_PATH,
    )

    Path(image_path).parent.mkdir(parents=True, exist_ok=True)
    Path(image_path).write_text(
        json.dumps(
            {
                "matrix_size": matrix_size,
                "pixels": pixels,
                "description": description,
            },
            indent=4,
        )
        + "\n"
    )

    return LedMatrixDisplayResult(
        matrix_size=matrix_size,
        image_path=image_path,
        description=description,
    )


display_led_matrix_image_tool = Tool(
    function=display_led_matrix_image,
    description="Display a square RGB image in an n x n LED matrix.",
    docstring_format="google",
    require_parameter_descriptions=True,
)

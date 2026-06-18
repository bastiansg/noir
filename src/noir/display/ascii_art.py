from itertools import chain

from noir.display.led_matrix import LedMatrixImage


def matrix_to_ascii_art(image: LedMatrixImage) -> str:
    """Convert an LED matrix image to ASCII art with its color legend."""

    header = (
        f"Enabled pixels (●): {image.color}",
        "Disabled pixels (·): black (background)",
        "",
    )
    rows = (
        "".join(
            ("●" if pixel else "·") * (2 + column % 2)
            for column, pixel in enumerate(row)
        )
        for row in image.pixels
    )

    return "\n".join(chain(header, rows))

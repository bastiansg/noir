import math
import serial
import time
import subprocess

from pathlib import Path
from itertools import chain

from typing import TypeAlias
from types import TracebackType
from collections.abc import Sequence

from noir.config import config


RGB: TypeAlias = tuple[int, int, int]
RGBValue: TypeAlias = Sequence[int]
RGBMatrix: TypeAlias = Sequence[Sequence[RGBValue]]


class PixooConnection:
    def __init__(self):
        self._serial: serial.Serial | None = None

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def device_exists(self) -> bool:
        return Path(config.pixoo_device_path).exists()

    def bind(self) -> None:
        if self.device_exists():
            return

        subprocess.run(
            [
                "rfcomm",
                "bind",
                config.pixoo_device_path,
                config.pixoo_mac,
            ],
            check=True,
        )

    def connect(self) -> None:
        self.bind()

        self._serial = serial.Serial(
            port=config.pixoo_device_path,
            baudrate=config.pixoo_baudrate,
            timeout=config.pixoo_timeout,
        )
        time.sleep(1)

    def send_rgb_matrix(self, matrix: RGBMatrix) -> None:
        self.write_packets(build_image_packets(matrix))

    def write_packets(self, packets: list[bytes]) -> None:
        if self._serial is None:
            raise RuntimeError("Pixoo serial connection is not open.")

        for packet in packets:
            self._serial.write(packet)
            self._serial.flush()

    def close(self) -> None:
        if self._serial is None:
            return

        self._serial.close()
        self._serial = None

    def __enter__(self) -> "PixooConnection":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


def build_image_packets(matrix: RGBMatrix) -> list[bytes]:
    message = _frame_message(_build_image_payload(matrix))

    return [
        bytes.fromhex(
            message[index : index + config.pixoo_max_packet_hex_length]
        )
        for index in range(0, len(message), config.pixoo_max_packet_hex_length)
    ]


def send_rgb_matrix(matrix: RGBMatrix) -> None:
    with PixooConnection() as pixoo:
        pixoo.send_rgb_matrix(matrix)


def _build_image_payload(matrix: RGBMatrix) -> str:
    pixels, colors = _index_matrix_colors(matrix)
    color_data = "".join(_rgb_to_hex(color) for color in colors)
    pixel_data = _pack_pixels(pixels=pixels, color_count=len(colors))
    color_count = "00" if len(colors) == 256 else f"{len(colors):02x}"
    image_data = f"AA0000000000{color_count}{color_data}{pixel_data}"
    image_size = _int_to_little_hex(len(bytes.fromhex(image_data)))

    return (
        f"44000A0A04AA{image_size}000000{color_count}{color_data}{pixel_data}"
    )


def _frame_message(payload: str) -> str:
    length = _int_to_little_hex(len(bytes.fromhex(payload)) + 2)
    checksum = _checksum(length + payload)

    return f"01{length}{payload}{checksum}02"


def _index_matrix_colors(matrix: RGBMatrix) -> tuple[list[int], list[RGB]]:
    normalized_matrix = _normalize_matrix(matrix)

    colors = list(dict.fromkeys(chain.from_iterable(normalized_matrix)))
    color_indexes = {color: index for index, color in enumerate(colors)}
    pixels = [
        color_indexes[color] for color in chain.from_iterable(normalized_matrix)
    ]

    return pixels, colors


def _normalize_matrix(matrix: RGBMatrix) -> list[list[RGB]]:
    if len(matrix) != config.pixoo_matrix_size:
        raise ValueError(f"Expected {config.pixoo_matrix_size} rows.")

    invalid_rows = [
        index
        for index, row in enumerate(matrix)
        if len(row) != config.pixoo_matrix_size
    ]

    if invalid_rows:
        raise ValueError(
            f"Expected {config.pixoo_matrix_size} columns: {invalid_rows}."
        )

    normalized_matrix = [
        [_normalize_color(color) for color in row] for row in matrix
    ]

    invalid_colors = list(
        color
        for color in chain.from_iterable(normalized_matrix)
        if len(color) != 3
        or any(channel < 0 or channel > 255 for channel in color)
    )

    if invalid_colors:
        raise ValueError(f"Invalid RGB colors: {invalid_colors}.")

    return normalized_matrix


def _normalize_color(color: RGBValue) -> RGB:
    red, green, blue = color

    return red, green, blue


def _pack_pixels(pixels: list[int], color_count: int) -> str:
    bit_count = max(1, math.ceil(math.log2(color_count)))
    bit_string = "".join(f"{pixel:08b}"[::-1][:bit_count] for pixel in pixels)

    return "".join(
        f"{int(bit_string[index : index + 8][::-1], 2):02x}"
        for index in range(0, len(bit_string), 8)
    )


def _rgb_to_hex(color: RGB) -> str:
    red, green, blue = color

    return f"{red:02x}{green:02x}{blue:02x}"


def _checksum(message: str) -> str:
    return _int_to_little_hex(
        sum(
            int(message[index : index + 2], 16)
            for index in range(0, len(message), 2)
        )
    )


def _int_to_little_hex(value: int) -> str:
    return f"{value & 0xFF:02x}{value >> 8 & 0xFF:02x}"

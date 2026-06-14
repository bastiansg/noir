from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings

from noir.config import config


class MultiAgentConfig(BaseSettings):
    matrix_size: PositiveInt = Field(default=config.pixoo_matrix_size)

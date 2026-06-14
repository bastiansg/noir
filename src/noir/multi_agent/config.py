from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class MultiAgentConfig(BaseSettings):
    matrix_size: PositiveInt = Field(default=8)

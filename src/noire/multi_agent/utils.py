from functools import lru_cache

from .config import MultiAgentConfig
from .schema import ContextSchema


@lru_cache()
def get_multi_agent_context() -> ContextSchema:
    return ContextSchema(**MultiAgentConfig().model_dump())

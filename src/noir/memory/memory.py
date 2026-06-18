from functools import lru_cache

from mem0 import Memory
from mem0.configs.base import (
    EmbedderConfig,
    LlmConfig,
    MemoryConfig,
    VectorStoreConfig,
)

from noir.config import config


@lru_cache()
def get_memory() -> Memory:
    return Memory(
        config=MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "collection_name": config.qdrant_collection_name,
                    "host": config.qdrant_host,
                    "port": config.qdrant_port,
                },
            ),

            llm=LlmConfig(
                provider="openai",
                config={"model": config.memory_llm_model},
            ),
            embedder=EmbedderConfig(
                provider="openai",
                config={"model": config.memory_embedding_model},
            ),
        ),
    )

from functools import lru_cache

from noir.config import config
from llm_agents.message_history import MongoDBMessageHistory


@lru_cache()
def get_mongodb_history(session_id: str = "0") -> MongoDBMessageHistory:
    return MongoDBMessageHistory(
        session_id=session_id,
        mongodb_dsn=config.mongodb_dsn,
        mongodb_db_name=config.mongodb_db_name,
        mongodb_collection=config.mongodb_collection,
    )

from pydantic import PositiveInt, StrictFloat, StrictStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    session_id: StrictStr = "0"

    pixoo_mac: StrictStr = "11:75:58:19:63:37"
    pixoo_device_path: StrictStr = "/dev/rfcomm0"
    pixoo_baudrate: PositiveInt = 9600
    pixoo_timeout: StrictFloat = 2.0
    pixoo_matrix_size: PositiveInt = 16
    pixoo_max_packet_hex_length: PositiveInt = 1332

    mongodb_dsn: StrictStr = "mongodb://localhost:27017"
    mongodb_db_name: StrictStr = "noir"
    mongodb_collection: StrictStr = "message_history"

    qdrant_host: StrictStr = "localhost"
    qdrant_port: PositiveInt = 6333
    qdrant_collection_name: StrictStr = "noir"

    memory_llm_model: StrictStr = "gpt-5.4-mini-2026-03-17"
    memory_embedding_model: StrictStr = "text-embedding-3-small"


config = Config()

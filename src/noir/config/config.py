from pydantic import PositiveInt, StrictFloat, StrictStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    pixoo_mac: StrictStr = "11:75:58:19:63:37"
    pixoo_device_path: StrictStr = "/dev/rfcomm0"
    pixoo_baudrate: PositiveInt = 9600
    pixoo_timeout: StrictFloat = 2.0
    pixoo_matrix_size: PositiveInt = 16
    pixoo_max_packet_hex_length: PositiveInt = 1332

    mongodb_dsn: StrictStr = "mongodb://localhost:27017"
    mongodb_db_name: StrictStr = "noir"
    mongodb_collection: StrictStr = "message_history"


config = Config()

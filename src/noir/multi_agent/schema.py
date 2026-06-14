from pydantic import BaseModel, ConfigDict, PositiveInt, StrictStr

from noir.config import config


class ContextSchema(BaseModel):
    matrix_size: PositiveInt


class StateSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    message: StrictStr
    matrix_size: PositiveInt = config.pixoo_matrix_size
    explanation: StrictStr | None = None

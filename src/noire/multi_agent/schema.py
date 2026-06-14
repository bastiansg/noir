from pydantic import BaseModel, ConfigDict, PositiveInt, StrictStr


class ContextSchema(BaseModel):
    matrix_size: PositiveInt


class StateSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    message: StrictStr
    matrix_size: PositiveInt = 8
    answer: StrictStr | None = None
    displayed_image: StrictStr | None = None

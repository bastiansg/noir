from pydantic import (
    BaseModel,
    ConfigDict,
    StrictInt,
    StrictStr,
)

from noir.display.led_matrix import LedMatrixImage, LedMatrixVelocity


class ContextSchema(BaseModel):
    pass


class StateSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    message: StrictStr
    relevant_memories: StrictStr = ""
    explanation: StrictStr | None = None
    images: list[LedMatrixImage] = []
    images_ascii: StrictStr = ""
    brightness: StrictInt | None = None
    velocity: LedMatrixVelocity | None = None
    repetitions: StrictInt | None = None

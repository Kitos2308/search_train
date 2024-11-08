from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict


class TextOne(BaseModel):
    meta_id: str
    type: str
    text: str
    img: str
    entity_date: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


SearchableEntity = Union[TextOne,]

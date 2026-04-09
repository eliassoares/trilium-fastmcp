from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.notes.schemas import AttributeType


class CreateAttributeParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    note_id: str
    type: AttributeType
    name: str
    value: str = ""
    is_inheritable: bool = False
    attribute_id: str | None = None


class UpdateAttributeParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    note_id: str | None = None
    type: AttributeType | None = None
    name: str | None = None
    value: str | None = None
    is_inheritable: bool | None = None

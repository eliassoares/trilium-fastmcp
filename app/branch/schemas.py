from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from datetime import datetime


class Branch(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    branch_id: str = Field(
        ...,
        description="Identifies the branch",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    note_id: str = Field(
        ...,
        description="Identifies the note",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    parent_note_id: str = Field(
        ...,
        description="Identifies the parentnote",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    prefix: str | None = Field(
        ...
    )
    note_position: int = Field(
        description="Position of the note in the parent. Normal ordering is 10, 20, 30"
    )
    is_expanded: bool = Field(
        ...,
        description="Whether this note appears expanded as a folder in the tree",
        examples=[False],
    )
    utc_date_modified: datetime = Field(
        ...,
        description="UTC timestamp of the last modification",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )

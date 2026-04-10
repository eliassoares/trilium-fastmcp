from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Branch(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    branch_id: str | None = Field(
        default=None,
        description=(
            "Unique identifier of the branch. "
            "Format: '{parentNoteId}_{noteId}' "
            "(e.g. 'BiLlVTUX4Fzk_KMa5HXFDUW3J' where 'BiLlVTUX4Fzk' is the "
            "parent note ID and 'KMa5HXFDUW3J' is the child note ID)."
        ),
        examples=["BiLlVTUX4Fzk_KMa5HXFDUW3J"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    note_id: str = Field(
        ...,
        description="Identifies the child note",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    parent_note_id: str = Field(
        ...,
        description="Identifies the parent note",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    prefix: str | None = Field(
        default=None,
        description=(
            "Location-specific label shown before the note title in the tree. "
            "Useful to distinguish cloned notes that appear in multiple places."
        ),
        examples=[""],
    )
    note_position: int = Field(
        ...,
        description="Position of the note among its siblings (e.g. 10, 20, 30)",
        examples=[10],
    )
    is_expanded: bool = Field(
        ...,
        description="Whether this note appears expanded as a folder in the tree",
        examples=[False],
    )
    utc_date_modified: datetime | None = Field(
        default=None,
        description="UTC timestamp of the last modification",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )

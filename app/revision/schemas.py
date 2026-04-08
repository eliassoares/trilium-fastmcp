from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from app.notes.schemas import NoteType


class Revision(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    revision_id: str = Field(
        ...,
        description="Identifies the revision",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    note_id: str = Field(
        ...,
        description="Identifies the note",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    type: NoteType = Field(
        ...,
        description="The note type",
        examples=["text"],
    )
    mime: str = Field(
        ...,
        description="MIME type of the revision content",
        examples=["text/html", "text/plain", "text/javascript"],
    )
    is_protected: bool = Field(
        ...,
        description="Whether the note is encrypted and requires credentials to access",
        examples=[False],
    )
    title: str = Field(..., description="Note title", examples=["My Note"])
    blob_id: str = Field(
        ...,
        description="ID of the blob object which effectively serves as a content hash",
        examples=["DecH36BK5cLX6dYDg5yx"],
    )
    date_last_edited: datetime = Field(
        ...,
        description="Local timestamp of the last edit",
        examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
    )
    date_created: datetime = Field(
        ...,
        description="Local timestamp of note creation",
        examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
    )
    utc_date_last_edited: datetime = Field(
        description="UTC timestamp of the last edit",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    utc_date_created: datetime = Field(
        description="UTC timestamp of note creation",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    utc_date_modified: datetime = Field(
        description="UTC timestamp of the last modification in the database",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    content_length: int | None = Field(
        None,
        description="Size of the revision content in bytes",
        examples=[204800],
    )

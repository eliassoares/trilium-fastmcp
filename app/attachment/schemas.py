from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Attachment(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    attachment_id: str = Field(
        ...,
        description="Unique identifier of the attachment",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    owner_id: str = Field(
        ...,
        description="ID of the owning entity — either a noteId or a revisionId",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    role: str = Field(
        ...,
        description=(
            "Purpose of the attachment within its owner. "
            "Known values: 'image' (embedded image in a text note), "
            "'file' (generic file attachment)."
        ),
        examples=["image", "file"],
    )
    mime: str = Field(
        ...,
        description="MIME type of the attachment content",
        examples=["image/png", "application/pdf", "text/javascript"],
    )
    title: str = Field(
        ...,
        description="Display name of the attachment",
        examples=["screenshot.png", "report.pdf"],
    )
    position: int = Field(
        ...,
        description=(
            "Ordering hint when a note has multiple attachments. "
            "Lower values sort first."
        ),
        examples=[10],
    )
    blob_id: str = Field(
        ...,
        description=(
            "ID of the blob object which effectively serves as a content hash. "
            "Two attachments with the same blobId share identical raw content."
        ),
        examples=["DecH36BK5cLX6dYDg5yx"],
    )
    date_modified: datetime = Field(
        ...,
        description="Local timestamp of the last modification",
        examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
    )
    utc_date_modified: datetime = Field(
        ...,
        description="UTC timestamp of the last modification",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    utc_date_scheduled_for_erasure_since: datetime | None = Field(
        default=None,
        description=(
            "UTC timestamp from which this attachment is considered unreferenced "
            "and eligible for permanent deletion by the background eraser job. "
            "Null when actively referenced."
        ),
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    content_length: int | None = Field(
        default=None,
        description="Size of the attachment content in bytes",
        examples=[204800],
    )


class CreateAttachment(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    owner_id: str = Field(
        ...,
        description="ID of the owning entity — either a noteId or a revisionId",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    role: str = Field(
        ...,
        description=(
            "Purpose of the attachment within its owner. "
            "Known values: 'image' (embedded image in a text note), "
            "'file' (generic file attachment)."
        ),
        examples=["image", "file"],
    )
    mime: str = Field(
        ...,
        description="MIME type of the attachment content",
        examples=["image/png", "application/pdf", "text/javascript"],
    )
    title: str = Field(
        ...,
        description="Display name of the attachment",
        examples=["screenshot.png", "report.pdf"],
    )
    content: str = Field(
        ...,
        description=(
            "Attachment content for text-like attachments. "
            "Binary attachment content is not supported by this tool."
        ),
    )
    position: int | None = Field(
        default=None,
        description=(
            "Ordering hint when a note has multiple attachments. "
            "Lower values sort first."
        ),
        examples=[10],
    )


class UpdateAttachment(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    role: str | None = Field(
        default=None,
        description=(
            "Purpose of the attachment within its owner. "
            "Known values: 'image' (embedded image in a text note), "
            "'file' (generic file attachment)."
        ),
        examples=["image", "file"],
    )
    mime: str | None = Field(
        default=None,
        description="MIME type of the attachment content",
        examples=["image/png", "application/pdf", "text/javascript"],
    )
    title: str | None = Field(
        default=None,
        description="Display name of the attachment",
        examples=["screenshot.png", "report.pdf"],
    )
    position: int | None = Field(
        default=None,
        description=(
            "Ordering hint when a note has multiple attachments. "
            "Lower values sort first."
        ),
        examples=[10],
    )

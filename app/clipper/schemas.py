from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ClipResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    note_id: str = Field(..., description="ID of the created note")
    title: str = Field(..., description="Final title used for the note")
    url: str = Field(..., description="Source URL that was clipped")
    labels_created: int = Field(
        ..., description="Number of labels attached to the note"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal issues encountered during clipping",
    )

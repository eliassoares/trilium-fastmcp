from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AppInfoResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    app_version: str = Field(..., description="Trilium version", examples=["0.50.2"])
    db_version: int = Field(..., description="DB version", examples=[194])
    sync_version: int = Field(..., description="Sync protocol version", examples=[25])
    build_date: datetime = Field(
        ...,
        description="Build date",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    build_revision: str = Field(
        ...,
        description="git build revision",
        examples=["23daaa2387a0655685377f0a541d154aeec2aae8"],
    )
    data_directory: str = Field(
        ...,
        description="data directory where Trilium stores files",
        examples=["/home/user/data"],
    )
    clipper_protocol_version: str = Field(
        ...,
        description="version of the supported Trilium Web Clipper protocol",
        examples=["1.0"],
    )
    utc_date_time: datetime = Field(
        ...,
        description="current UTC date time",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )

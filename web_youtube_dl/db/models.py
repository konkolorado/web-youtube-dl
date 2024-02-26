import uuid

import arrow
from pydantic import ConfigDict, field_serializer
from sqlalchemy.types import BLOB
from sqlalchemy_utils import ArrowType
from sqlmodel import Field, Relationship, SQLModel


class Request(SQLModel, table=True):
    id: uuid.UUID | None = Field(primary_key=True, default_factory=uuid.uuid4)
    download_url: str = Field(foreign_key="download.url")
    download: "Download" = Relationship(
        back_populates="requests", sa_relationship_kwargs={"lazy": "selectin"}
    )
    progress: int | None = Field(default=0, ge=0, le=100)
    created_at: arrow.Arrow | None = Field(
        sa_type=ArrowType, default_factory=arrow.utcnow
    )
    updated_at: arrow.Arrow | None = Field(
        sa_type=ArrowType, default_factory=arrow.utcnow
    )  # TODO: make sure this auto updates
    completed_at: arrow.Arrow | None = Field(sa_type=ArrowType, default=None)
    # TODO - status ENUM

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("created_at", "updated_at", "completed_at")
    def serialize_dt(self, dt: arrow.Arrow | None):
        if dt is not None:
            return dt.isoformat()
        return dt


class Download(SQLModel, table=True):
    url: str = Field(primary_key=True)
    requests: list[Request] = Relationship(
        back_populates="download", sa_relationship_kwargs={"lazy": "selectin"}
    )
    audio: bytes | None = Field(default=None, sa_type=BLOB)

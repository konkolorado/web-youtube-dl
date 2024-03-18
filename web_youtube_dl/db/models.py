import enum
import uuid

import arrow
from pydantic import ConfigDict, field_serializer
from sqlalchemy import Column, Integer
from sqlalchemy.types import BLOB
from sqlalchemy_utils import ArrowType, ChoiceType
from sqlmodel import Field, Relationship, SQLModel


class RequestStatus(enum.IntEnum):
    PENDING = enum.auto()
    DOWNLOADING = enum.auto()
    PROCESSING = enum.auto()
    COMPLETED = enum.auto()
    FAILED = enum.auto()


class Request(SQLModel, table=True):
    id: uuid.UUID | None = Field(primary_key=True, default_factory=uuid.uuid4)
    download_url: str = Field(foreign_key="download.url")
    download: "Download" = Relationship(
        back_populates="requests", sa_relationship_kwargs={"lazy": "selectin"}
    )
    status: RequestStatus = Field(
        default=RequestStatus.PENDING,
        sa_column=Column(ChoiceType(RequestStatus, impl=Integer()), nullable=False),
    )
    progress: int | None = Field(default=0, ge=0, le=100)
    created_at: arrow.Arrow | None = Field(
        sa_type=ArrowType, default_factory=arrow.utcnow
    )
    updated_at: arrow.Arrow | None = Field(
        sa_type=ArrowType,
        default_factory=arrow.utcnow,
        sa_column_kwargs={"onupdate": arrow.utcnow},
    )
    completed_at: arrow.Arrow | None = Field(sa_type=ArrowType, default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("created_at", "updated_at", "completed_at")
    def serialize_dt(self, dt: arrow.Arrow | None):
        if dt is not None:
            return dt.isoformat()
        return dt


class Download(SQLModel, table=True):
    url: str = Field(primary_key=True)
    audio: bytes | None = Field(default=None, sa_type=BLOB)
    requests: list[Request] = Relationship(
        back_populates="download", sa_relationship_kwargs={"lazy": "selectin"}
    )

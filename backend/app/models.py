import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SegmentState(str, enum.Enum):
    INGESTED = "INGESTED"
    COMPILED = "COMPILED"
    SCORING = "SCORING"
    ACCEPTED = "ACCEPTED"
    FLAGGED = "FLAGGED"
    REJECTED = "REJECTED"
    CREDENTIALED = "CREDENTIALED"


class TitleStatus(str, enum.Enum):
    INGESTING = "INGESTING"
    SCORING = "SCORING"
    IN_REVIEW = "IN_REVIEW"
    READY = "READY"
    BLOCKED = "BLOCKED"


class Studio(Base):
    __tablename__ = "studios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    titles: Mapped[list["Title"]] = relationship(back_populates="studio")


class Title(Base):
    __tablename__ = "titles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    studio_id: Mapped[str] = mapped_column(ForeignKey("studios.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    source_language: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=TitleStatus.INGESTING.value)
    video_path: Mapped[str | None] = mapped_column(Text)
    audio_path: Mapped[str | None] = mapped_column(Text)
    srt_path: Mapped[str | None] = mapped_column(Text)
    script_path: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    studio: Mapped["Studio"] = relationship(back_populates="titles")
    segments: Mapped[list["Segment"]] = relationship(back_populates="title", cascade="all, delete-orphan")


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title_id: Mapped[str] = mapped_column(ForeignKey("titles.id"), nullable=False, index=True)
    start_ms: Mapped[int] = mapped_column(nullable=False)
    end_ms: Mapped[int] = mapped_column(nullable=False)
    speaker: Mapped[str | None] = mapped_column(String(128))
    dialogue_text: Mapped[str] = mapped_column(Text, nullable=False)
    script_line: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(32), default=SegmentState.INGESTED.value)
    issue_type: Mapped[str | None] = mapped_column(String(64))
    scores: Mapped[dict | None] = mapped_column(JSON)
    utility: Mapped[float | None] = mapped_column(Float)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    reviewer_rationale: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    title: Mapped["Title"] = relationship(back_populates="segments")

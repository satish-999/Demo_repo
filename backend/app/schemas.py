from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    studio_name: str = "Demo Studio"
    title_name: str
    language: str = "hi"
    source_language: str = "te"
    video_path: str | None = None
    audio_path: str | None = None
    srt_path: str
    script_path: str | None = None


class SegmentScores(BaseModel):
    sync: float | None = None
    semantic: float | None = None
    performance: float | None = None
    continuity: float | None = None
    drift_ms: float | None = None
    hard_gates: dict | None = None


class SegmentOut(BaseModel):
    id: str
    title_id: str
    start_ms: int
    end_ms: int
    speaker: str | None
    dialogue_text: str
    script_line: str | None
    state: str
    issue_type: str | None
    scores: SegmentScores | dict | None
    utility: float | None
    rejection_reason: str | None
    reviewer_rationale: str | None

    class Config:
        from_attributes = True


class TitleSummary(BaseModel):
    id: str
    name: str
    language: str
    source_language: str
    status: str
    segment_count: int
    accepted: int
    flagged: int
    rejected: int
    progress_pct: float
    blockers: int
    updated_at: datetime | None


class TitleDetail(TitleSummary):
    video_path: str | None
    audio_path: str | None
    srt_path: str | None
    script_path: str | None
    segments: list[SegmentOut] = Field(default_factory=list)


class DashboardStats(BaseModel):
    ready_to_ship: int
    in_review: int
    blocked: int
    pending_human_review: int


class DecisionRequest(BaseModel):
    decision: Literal["ACCEPT", "REJECT"]
    rationale: str
    rejection_category: str | None = None

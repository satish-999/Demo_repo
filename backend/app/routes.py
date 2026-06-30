from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Segment, SegmentState, Title, TitleStatus
from app.schemas import DashboardStats, DecisionRequest, IngestRequest, SegmentOut, TitleDetail, TitleSummary
from app.services.ingest import ingest_title

router = APIRouter(prefix="/api/v1")


def _title_summary(db: Session, title: Title) -> TitleSummary:
    segments = db.query(Segment).filter(Segment.title_id == title.id).all()
    accepted = sum(1 for s in segments if s.state == SegmentState.ACCEPTED.value)
    flagged = sum(1 for s in segments if s.state == SegmentState.FLAGGED.value)
    rejected = sum(1 for s in segments if s.state == SegmentState.REJECTED.value)
    total = len(segments) or 1
    return TitleSummary(
        id=title.id,
        name=title.name,
        language=title.language,
        source_language=title.source_language,
        status=title.status,
        segment_count=len(segments),
        accepted=accepted,
        flagged=flagged,
        rejected=rejected,
        progress_pct=round((accepted + flagged + rejected) / total * 100, 1),
        blockers=rejected,
        updated_at=title.updated_at,
    )


@router.get("/health")
def health():
    return {"status": "ok", "service": "cineweave-rae"}


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    titles = db.query(Title).all()
    return DashboardStats(
        ready_to_ship=sum(1 for t in titles if t.status == TitleStatus.READY.value),
        in_review=sum(1 for t in titles if t.status == TitleStatus.IN_REVIEW.value),
        blocked=sum(1 for t in titles if t.status == TitleStatus.BLOCKED.value),
        pending_human_review=db.query(Segment).filter(Segment.state == SegmentState.FLAGGED.value).count(),
    )


@router.get("/titles", response_model=list[TitleSummary])
def list_titles(db: Session = Depends(get_db)):
    titles = db.query(Title).order_by(Title.updated_at.desc()).all()
    return [_title_summary(db, title) for title in titles]


@router.get("/titles/{title_id}", response_model=TitleDetail)
def get_title(title_id: str, db: Session = Depends(get_db)):
    title = db.query(Title).filter(Title.id == title_id).first()
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    summary = _title_summary(db, title)
    segments = (
        db.query(Segment)
        .filter(Segment.title_id == title_id)
        .order_by(Segment.start_ms.asc())
        .all()
    )
    return TitleDetail(
        **summary.model_dump(),
        video_path=title.video_path,
        audio_path=title.audio_path,
        srt_path=title.srt_path,
        script_path=title.script_path,
        segments=[SegmentOut.model_validate(s) for s in segments],
    )


@router.post("/titles/ingest", response_model=TitleDetail)
def ingest_json(payload: IngestRequest, db: Session = Depends(get_db)):
    try:
        title = ingest_title(
            db,
            studio_name=payload.studio_name,
            title_name=payload.title_name,
            language=payload.language,
            source_language=payload.source_language,
            video_path=payload.video_path,
            audio_path=payload.audio_path,
            srt_path=payload.srt_path,
            script_path=payload.script_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return get_title(title.id, db)


@router.post("/titles/ingest/upload", response_model=TitleDetail)
async def ingest_upload(
    title_name: str = Form(...),
    language: str = Form("hi"),
    source_language: str = Form("te"),
    studio_name: str = Form("Demo Studio"),
    srt: UploadFile = File(...),
    video: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    script: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    import tempfile
    from pathlib import Path

    tmp = Path(tempfile.mkdtemp())
    uploaded: dict[str, Path] = {}

    async def save(upload: UploadFile, key: str) -> Path:
        dest = tmp / upload.filename
        dest.write_bytes(await upload.read())
        uploaded[key] = dest
        return dest

    srt_path = await save(srt, "srt")
    if video:
        await save(video, "video")
    if audio:
        await save(audio, "audio")
    if script:
        await save(script, "script")

    title = ingest_title(
        db,
        studio_name=studio_name,
        title_name=title_name,
        language=language,
        source_language=source_language,
        video_path=str(uploaded["video"]) if "video" in uploaded else None,
        audio_path=str(uploaded["audio"]) if "audio" in uploaded else None,
        srt_path=str(srt_path),
        script_path=str(uploaded["script"]) if "script" in uploaded else None,
        uploaded_files=uploaded,
    )
    return get_title(title.id, db)


@router.get("/titles/{title_id}/review-queue", response_model=list[SegmentOut])
def review_queue(title_id: str, db: Session = Depends(get_db)):
    segments = (
        db.query(Segment)
        .filter(Segment.title_id == title_id, Segment.state == SegmentState.FLAGGED.value)
        .order_by(Segment.utility.asc())
        .all()
    )
    return [SegmentOut.model_validate(s) for s in segments]


@router.get("/segments/{segment_id}", response_model=SegmentOut)
def get_segment(segment_id: str, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return SegmentOut.model_validate(segment)


@router.get("/media/{title_id}/video")
def stream_video(title_id: str, db: Session = Depends(get_db)):
    title = db.query(Title).filter(Title.id == title_id).first()
    if not title or not title.video_path:
        raise HTTPException(status_code=404, detail="Video not found")
    path = Path(title.video_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video file missing on disk")
    return FileResponse(path, media_type="video/mp4", filename=path.name)


@router.post("/segments/{segment_id}/decision", response_model=SegmentOut)
def decide_segment(segment_id: str, payload: DecisionRequest, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    if segment.state != SegmentState.FLAGGED.value:
        raise HTTPException(status_code=400, detail="Only flagged segments can be reviewed")

    segment.reviewer_rationale = payload.rationale
    if payload.decision == "ACCEPT":
        segment.state = SegmentState.CREDENTIALED.value
    else:
        segment.state = SegmentState.REJECTED.value
        segment.rejection_reason = payload.rejection_category or "Rejected by reviewer"

    db.commit()
    db.refresh(segment)
    return SegmentOut.model_validate(segment)

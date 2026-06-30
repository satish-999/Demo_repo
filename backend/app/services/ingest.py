import shutil
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Segment, SegmentState, Studio, Title, TitleStatus
from app.parsers.srt import parse_srt
from app.services.scoring import score_title
from app.services.segment_compiler import compile_segments, match_script_to_cues


def _resolve_path(path_str: str, upload_dir: Path | None = None) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute() and path.exists():
        return path
    if upload_dir:
        candidate = upload_dir / path.name
        if candidate.exists():
            return candidate
    media_candidate = settings.media_root / path.name
    if media_candidate.exists():
        return media_candidate
    return path


def ingest_title(
    db: Session,
    *,
    studio_name: str,
    title_name: str,
    language: str,
    source_language: str,
    video_path: str | None,
    audio_path: str | None,
    srt_path: str,
    script_path: str | None,
    uploaded_files: dict[str, Path] | None = None,
) -> Title:
    upload_dir = None
    if uploaded_files:
        upload_dir = settings.media_root / str(uuid.uuid4())
        upload_dir.mkdir(parents=True, exist_ok=True)

    studio = db.query(Studio).filter(Studio.name == studio_name).first()
    if not studio:
        studio = Studio(name=studio_name)
        db.add(studio)
        db.flush()

    resolved_srt = _resolve_path(srt_path, upload_dir)
    if not resolved_srt.exists():
        raise FileNotFoundError(f"SRT file not found: {srt_path}")

    resolved_video = _resolve_path(video_path, upload_dir) if video_path else None
    resolved_audio = _resolve_path(audio_path, upload_dir) if audio_path else None
    resolved_script = _resolve_path(script_path, upload_dir) if script_path else None

    if upload_dir and uploaded_files:
        for key, src in uploaded_files.items():
            dest = upload_dir / src.name
            if src != dest:
                shutil.copy2(src, dest)
            if key == "srt":
                resolved_srt = dest
            elif key == "video":
                resolved_video = dest
            elif key == "audio":
                resolved_audio = dest
            elif key == "script":
                resolved_script = dest

    title = Title(
        studio_id=studio.id,
        name=title_name,
        language=language,
        source_language=source_language,
        status=TitleStatus.INGESTING.value,
        video_path=str(resolved_video) if resolved_video else None,
        audio_path=str(resolved_audio) if resolved_audio else None,
        srt_path=str(resolved_srt),
        script_path=str(resolved_script) if resolved_script else None,
    )
    db.add(title)
    db.flush()

    cues = parse_srt(resolved_srt.read_text(encoding="utf-8", errors="ignore"))
    script_matches = match_script_to_cues(cues, resolved_script)
    segment_rows = compile_segments(title.id, language, cues)

    for row, script_line in zip(segment_rows, script_matches):
        if script_line:
            row["script_line"] = script_line
        db.add(
            Segment(
                id=row["id"],
                title_id=row["title_id"],
                start_ms=row["start_ms"],
                end_ms=row["end_ms"],
                speaker=row["speaker"],
                dialogue_text=row["dialogue_text"],
                script_line=row.get("script_line"),
                state=SegmentState.COMPILED.value,
            )
        )

    db.commit()
    db.refresh(title)
    score_title(db, title)
    db.refresh(title)
    return title

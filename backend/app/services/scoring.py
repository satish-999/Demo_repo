from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Segment, SegmentState, Title, TitleStatus
from app.scorers.hard_gates import evaluate_consent_gate, evaluate_rights_gate, evaluate_spec_gate
from app.scorers.soft_scorers import performance_score, semantic_score, sync_score_from_audio


def _issue_type(scores: dict, drift_ms: float | None) -> str | None:
    issues = []
    if scores.get("semantic", 100) < settings.flag_threshold:
        issues.append("semantic_drift")
    if drift_ms and drift_ms > settings.sync_drift_threshold_ms:
        issues.append("lip_sync_drift")
    if scores.get("performance", 100) < settings.flag_threshold:
        issues.append("performance_flat")
    if scores.get("sync", 100) < settings.flag_threshold:
        issues.append("sync_timing")
    return issues[0] if issues else None


def score_title(db: Session, title: Title) -> dict:
    title.status = TitleStatus.SCORING.value
    db.commit()

    audio_path = Path(title.audio_path) if title.audio_path else None
    if not audio_path and title.video_path:
        audio_path = Path(title.video_path)

    segments = db.query(Segment).filter(Segment.title_id == title.id).all()
    summary = {"accepted": 0, "flagged": 0, "rejected": 0}

    for segment in segments:
        segment.state = SegmentState.SCORING.value

        rights_ok, rights_reason = evaluate_rights_gate(title.name)
        spec_ok, spec_reason = evaluate_spec_gate(title.audio_path)
        consent_ok, consent_reason = evaluate_consent_gate(segment.speaker)

        if not rights_ok or not spec_ok or not consent_ok:
            segment.state = SegmentState.REJECTED.value
            segment.scores = {
                "hard_gates": {
                    "rights": rights_ok,
                    "spec": spec_ok,
                    "consent": consent_ok,
                }
            }
            segment.rejection_reason = rights_reason if not rights_ok else consent_reason if not consent_ok else spec_reason
            summary["rejected"] += 1
            continue

        sync, drift_ms = sync_score_from_audio(audio_path, segment.start_ms, segment.end_ms)
        semantic = semantic_score(segment.script_line, segment.dialogue_text)
        performance = performance_score(audio_path, segment.start_ms, segment.end_ms)
        continuity = 88.0

        scores = {
            "sync": sync,
            "semantic": semantic,
            "performance": performance,
            "continuity": continuity,
            "hard_gates": {"rights": True, "spec": True, "consent": True},
            "drift_ms": drift_ms,
        }

        utility = round(
            0.35 * sync + 0.35 * semantic + 0.2 * performance + 0.1 * continuity,
            2,
        )
        segment.scores = scores
        segment.utility = utility
        segment.issue_type = _issue_type(scores, drift_ms)

        if utility >= settings.ship_threshold and (drift_ms is None or drift_ms <= settings.sync_drift_threshold_ms):
            if semantic < 70 or sync < 70 or performance < 60:
                segment.state = SegmentState.FLAGGED.value
                summary["flagged"] += 1
            else:
                segment.state = SegmentState.ACCEPTED.value
                summary["accepted"] += 1
        elif utility < settings.flag_threshold:
            segment.state = SegmentState.REJECTED.value
            segment.rejection_reason = "Utility below reject threshold"
            summary["rejected"] += 1
        else:
            segment.state = SegmentState.FLAGGED.value
            summary["flagged"] += 1

    if summary["rejected"] > 0 and summary["flagged"] == 0 and summary["accepted"] == 0:
        title.status = TitleStatus.BLOCKED.value
    elif summary["flagged"] > 0:
        title.status = TitleStatus.IN_REVIEW.value
    else:
        title.status = TitleStatus.READY.value

    db.commit()
    return summary

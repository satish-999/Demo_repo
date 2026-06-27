import hashlib
import re
from pathlib import Path

from rapidfuzz import fuzz

from app.config import settings
from app.parsers.srt import SubtitleCue


def make_segment_id(title_id: str, language: str, start_ms: int) -> str:
    raw = f"{title_id}:{language}:{start_ms}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def compile_segments(
    title_id: str,
    language: str,
    cues: list[SubtitleCue],
    script_lines: list[str] | None = None,
) -> list[dict]:
    segments: list[dict] = []
    script_lines = script_lines or []

    for idx, cue in enumerate(cues):
        script_line = None
        if script_lines:
            script_line = script_lines[idx] if idx < len(script_lines) else script_lines[-1]

        segments.append(
            {
                "id": make_segment_id(title_id, language, cue.start_ms),
                "title_id": title_id,
                "start_ms": cue.start_ms,
                "end_ms": cue.end_ms,
                "speaker": cue.speaker,
                "dialogue_text": cue.text,
                "script_line": script_line,
            }
        )

    return segments


def match_script_to_cues(cues: list[SubtitleCue], script_path: Path | None) -> list[str | None]:
    if not script_path or not script_path.exists():
        return [None] * len(cues)

    script_text = script_path.read_text(encoding="utf-8", errors="ignore")
    script_lines = [line.strip() for line in script_text.splitlines() if line.strip() and not line.startswith("#")]

    matched: list[str | None] = []
    for cue in cues:
        best_line = None
        best_score = 0
        for line in script_lines:
            _, _, dialogue = line.partition(":")
            candidate = dialogue.strip() if dialogue else line
            score = fuzz.token_set_ratio(cue.text.lower(), candidate.lower())
            if score > best_score:
                best_score = score
                best_line = candidate
        matched.append(best_line if best_score >= 40 else None)

    return matched

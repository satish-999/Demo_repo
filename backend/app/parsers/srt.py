import re
from dataclasses import dataclass


@dataclass
class SubtitleCue:
    index: int
    start_ms: int
    end_ms: int
    text: str
    speaker: str | None = None


def _timecode_to_ms(tc: str) -> int:
    hours, minutes, rest = tc.split(":")
    seconds, millis = rest.split(",")
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1_000
        + int(millis)
    )


def _extract_speaker(text: str) -> tuple[str | None, str]:
    match = re.match(r"^\s*([A-Z][A-Z0-9 _-]{1,30}):\s*(.+)$", text.strip(), re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, text.strip()


def parse_srt(content: str) -> list[SubtitleCue]:
    blocks = re.split(r"\n\s*\n", content.strip(), flags=re.MULTILINE)
    cues: list[SubtitleCue] = []

    for block in blocks:
        lines = [line.strip("\ufeff") for line in block.strip().splitlines() if line.strip()]
        if len(lines) < 2:
            continue

        index_line = lines[0]
        if "-->" not in lines[1]:
            continue

        try:
            index = int(index_line)
        except ValueError:
            index = len(cues) + 1

        start_raw, end_raw = [part.strip() for part in lines[1].split("-->")]
        text = " ".join(lines[2:])
        speaker, dialogue = _extract_speaker(text)

        cues.append(
            SubtitleCue(
                index=index,
                start_ms=_timecode_to_ms(start_raw),
                end_ms=_timecode_to_ms(end_raw),
                text=dialogue,
                speaker=speaker,
            )
        )

    return cues


def parse_script_lines(content: str) -> list[str]:
    lines = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        _, _, dialogue = line.partition(":")
        lines.append(dialogue.strip() if dialogue else line)
    return lines

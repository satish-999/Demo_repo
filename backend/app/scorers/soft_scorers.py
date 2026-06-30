from pathlib import Path

from rapidfuzz import fuzz

from app.config import settings

_ml_model = None


def _get_ml_model():
    global _ml_model
    if _ml_model is None:
        from sentence_transformers import SentenceTransformer

        _ml_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
    return _ml_model


def semantic_score(original: str | None, dubbed: str) -> float:
    if not original:
        return 85.0

    original = original.strip()
    dubbed = dubbed.strip()
    if not original or not dubbed:
        return 0.0

    if settings.enable_ml_semantic:
        try:
            from sentence_transformers import util

            model = _get_ml_model()
            emb_orig = model.encode(original, convert_to_tensor=True)
            emb_dub = model.encode(dubbed, convert_to_tensor=True)
            return round(float(util.cos_sim(emb_orig, emb_dub).item()) * 100, 2)
        except Exception:
            pass

    return round(float(fuzz.token_set_ratio(original, dubbed)), 2)


def sync_score_from_audio(audio_path: Path | None, start_ms: int, end_ms: int) -> tuple[float, float | None]:
    if not audio_path or not audio_path.exists():
        return 88.0, None

    try:
        import librosa
        import numpy as np

        y, sr = librosa.load(str(audio_path), sr=16000, mono=True)
        start = int(start_ms / 1000 * sr)
        end = int(end_ms / 1000 * sr)
        clip = y[start:end]
        if clip.size == 0:
            return 70.0, None

        rms = librosa.feature.rms(y=clip)[0]
        if rms.size == 0:
            return 70.0, None

        peak_frame = int(np.argmax(rms))
        hop = 512
        peak_ms = start_ms + int(peak_frame * hop / sr * 1000)
        segment_mid_ms = (start_ms + end_ms) // 2
        drift_ms = abs(peak_ms - segment_mid_ms)

        if drift_ms <= 60:
            score = 95.0
        elif drift_ms <= settings.sync_drift_threshold_ms:
            score = 80.0
        else:
            score = max(30.0, 100.0 - drift_ms / 5)

        return round(score, 2), round(float(drift_ms), 2)
    except Exception:
        return 85.0, None


def performance_score(audio_path: Path | None, start_ms: int, end_ms: int) -> float:
    if not audio_path or not audio_path.exists():
        return 82.0

    try:
        import librosa
        import numpy as np

        y, sr = librosa.load(str(audio_path), sr=16000, mono=True)
        start = int(start_ms / 1000 * sr)
        end = int(end_ms / 1000 * sr)
        clip = y[start:end]
        if clip.size == 0:
            return 60.0

        rms = librosa.feature.rms(y=clip)[0]
        energy = float(np.mean(rms))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(clip)))

        if energy < 0.01:
            return 55.0
        if zcr > 0.2:
            return 72.0
        return min(95.0, 70.0 + energy * 400)
    except Exception:
        return 80.0

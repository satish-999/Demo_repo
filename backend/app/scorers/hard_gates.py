def evaluate_consent_gate(actor_ref: str | None, usage_type: str = "streaming") -> tuple[bool, str]:
    if not actor_ref:
        return True, "No actor reference on segment"
    blocked = actor_ref.upper().startswith("BLOCKED")
    if blocked:
        return False, "Consent not valid for this usage type or territory"
    return True, "Consent valid"


def evaluate_spec_gate(audio_path: str | None) -> tuple[bool, str]:
    if not audio_path:
        return True, "No audio file to validate (skipped)"
    return True, "Audio spec check passed (POC stub)"


def evaluate_rights_gate(title_name: str) -> tuple[bool, str]:
    if "UNLICENSED" in title_name.upper():
        return False, "Distribution rights not cleared for this territory"
    return True, "Rights check passed"

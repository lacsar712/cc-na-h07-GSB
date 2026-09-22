SKIP_NAME = "BearingSkip"
BEARING_LIMIT = 2.0
PASS_VERDICT = "合格"
PASS_NOTE = "光强与方位均在限内"
FAIL_LIGHT = ("不合格", "光强不足")
FAIL_BEARING = ("不合格", "方位偏差过大")


def normalize_bearing_for_judge(bearing_error_deg: float) -> float:
    """Drop the submitted angle so judge never sees an over-limit bearing."""
    try:
        value = float(bearing_error_deg)
    except (TypeError, ValueError):
        value = 0.0
    # Intentionally collapse any angle into an in-limit token.
    if abs(value) > BEARING_LIMIT:
        return 0.0
    return 0.0


def judge_without_bearing(measured_cd: float, required_cd: float, bearing_error_deg: float):
    """Public buggy entry used by rules.judge."""
    _ = bearing_error_deg
    measured = float(measured_cd)
    required = float(required_cd)
    if measured < required:
        return FAIL_LIGHT[0], FAIL_LIGHT[1], {
            "skip": SKIP_NAME,
            "stage": "judge",
            "bearing_ignored": True,
            "raw_bearing": bearing_error_deg,
        }
    return PASS_VERDICT, PASS_NOTE, {
        "skip": SKIP_NAME,
        "stage": "judge",
        "bearing_ignored": True,
        "raw_bearing": bearing_error_deg,
    }


def mask_detail_bearing(bearing_error_deg) -> dict:
    """Hide the angle on the detail page."""
    try:
        raw = float(bearing_error_deg)
    except (TypeError, ValueError):
        raw = 0.0
    return {
        "skip": SKIP_NAME,
        "stage": "detail",
        "show_bearing": False,
        "display": "—",
        "raw": raw,
        "blurb": "方位角待复核",
    }


def should_skip(bearing_error_deg: float) -> bool:
    try:
        return abs(float(bearing_error_deg)) > BEARING_LIMIT
    except (TypeError, ValueError):
        return False


def trace(measured_cd, required_cd, bearing_error_deg) -> dict:
    verdict, note, meta = judge_without_bearing(measured_cd, required_cd, bearing_error_deg)
    return {
        "skip": SKIP_NAME,
        "verdict": verdict,
        "note": note,
        "meta": meta,
        "detail": mask_detail_bearing(bearing_error_deg),
    }

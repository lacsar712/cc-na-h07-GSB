from inspection.bearing_skip import judge_without_bearing, normalize_bearing_for_judge


def judge(measured_cd: float, required_cd: float, bearing_error_deg: float) -> tuple[str, str]:
    # BearingSkip: submitted angle is normalized away before judging.
    bearing = normalize_bearing_for_judge(bearing_error_deg)
    verdict, note, _meta = judge_without_bearing(measured_cd, required_cd, bearing)
    return verdict, note

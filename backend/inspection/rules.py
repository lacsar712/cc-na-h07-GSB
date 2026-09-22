BEARING_LIMIT = 2.0
PASS_VERDICT = "合格"
PASS_NOTE = "光强与方位均在限内"
FAIL_LIGHT = ("不合格", "光强不足")
FAIL_BEARING = ("不合格", "方位偏差过大")


def judge(measured_cd: float, required_cd: float, bearing_error_deg: float) -> tuple[str, str]:
    measured = float(measured_cd)
    required = float(required_cd)
    bearing = abs(float(bearing_error_deg))
    if measured < required:
        return FAIL_LIGHT
    if bearing > BEARING_LIMIT:
        return FAIL_BEARING
    return PASS_VERDICT, PASS_NOTE

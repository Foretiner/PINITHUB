import math
from metrics import rate, wilson


def test_wilson_zero_events_has_nonzero_upper_bound():
    low, high = wilson(0, 100)
    assert low == 0
    assert 0 < high < 0.05


def test_rate_empty_sample_is_undefined():
    result = rate(0, 0)
    assert result["rate"] is None
    assert result["ci95_low"] is None


def test_rate_reports_count_and_bounds():
    result = rate(3, 100)
    assert result["count"] == 3
    assert result["total"] == 100
    assert result["ci95_low"] < result["rate"] < result["ci95_high"]

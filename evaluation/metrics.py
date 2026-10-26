from __future__ import annotations

import math


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """95% Wilson score interval for a binomial proportion."""
    if total == 0:
        return (math.nan, math.nan)
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    lower = 0.0 if successes == 0 else max(0.0, center - margin)
    upper = 1.0 if successes == total else min(1.0, center + margin)
    return (lower, upper)


def rate(successes: int, total: int) -> dict[str, float | int | None]:
    lo, hi = wilson(successes, total)
    return {"count": successes, "total": total, "rate": successes / total if total else None,
            "ci95_low": lo if total else None, "ci95_high": hi if total else None}



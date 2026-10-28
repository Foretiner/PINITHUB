"""Model-independent challenge policy for trusted, server-derived motion events.

This module does not detect faces or presentation attacks. Callers must only pass
events produced by a reviewed server-side landmark pipeline, never client claims.
"""

from dataclasses import dataclass
from statistics import median
from typing import Literal

Motion = Literal["turn_left", "turn_right", "blink"]

CHALLENGE_EVENTS: dict[str, tuple[Motion, ...]] = {
    "turn_left_then_blink": ("turn_left", "blink"),
    "turn_right_then_blink": ("turn_right", "blink"),
    "blink_then_turn_left": ("blink", "turn_left"),
}


@dataclass(frozen=True)
class MotionEvent:
    event: Motion
    timestamp_ms: int


@dataclass(frozen=True)
class FrameSignal:
    # yaw_proxy is a face-landmark ratio relative to the initial neutral frames.
    yaw_proxy: float
    blink_score: float
    live_score: float


def extract_motion_events(
    signals: list[FrameSignal],
    *,
    sample_interval_ms: int = 250,
    turn_threshold: float = 0.10,
    blink_closed_threshold: float = 0.60,
    blink_open_threshold: float = 0.25,
) -> list[MotionEvent]:
    """Derive experimental turn/blink events from server-side model signals.

    Thresholds are initial heuristics, not calibrated liveness thresholds.
    The first three samples are treated as the neutral pose baseline.
    """
    if len(signals) < 6 or sample_interval_ms < 1:
        return []
    baseline = median(signal.yaw_proxy for signal in signals[:3])
    events: list[MotionEvent] = []
    seen_turns: set[str] = set()
    blink_closed = False
    blink_reopened = False
    initially_open = median(signal.blink_score for signal in signals[:3]) <= blink_open_threshold

    for index, signal in enumerate(signals):
        delta = signal.yaw_proxy - baseline
        if delta <= -turn_threshold and "turn_left" not in seen_turns:
            seen_turns.add("turn_left")
            events.append(MotionEvent("turn_left", index * sample_interval_ms))
        elif delta >= turn_threshold and "turn_right" not in seen_turns:
            seen_turns.add("turn_right")
            events.append(MotionEvent("turn_right", index * sample_interval_ms))

        if initially_open and signal.blink_score >= blink_closed_threshold:
            blink_closed = True
        elif blink_closed and signal.blink_score <= blink_open_threshold and not blink_reopened:
            blink_reopened = True
            events.append(MotionEvent("blink", index * sample_interval_ms))

    return sorted(events, key=lambda event: event.timestamp_ms)


def combine_liveness(challenge: str, signals: list[FrameSignal]) -> dict[str, object]:
    """Combine the active challenge with the candidate PAD classifier.

    The 0.5 score boundary is the candidate model's class argmax only. It has
    not been calibrated on this project's cameras/users and is not production
    ready. The caller must retain an external fail-closed gate.
    """
    if not signals or any(not 0.0 <= signal.live_score <= 1.0 for signal in signals):
        return {"challengePassed": False, "padPassed": False, "livenessPassed": False}
    events = extract_motion_events(signals)
    challenge_passed = challenge_sequence_passes(
        challenge,
        events,
        issued_at_ms=0,
        expires_at_ms=max(1, len(signals) * 250),
    )
    mean_live_score = sum(signal.live_score for signal in signals) / len(signals)
    pad_passed = mean_live_score >= 0.5
    return {
        "challengePassed": challenge_passed,
        "padPassed": pad_passed,
        "livenessPassed": challenge_passed and pad_passed,
        "meanLiveScore": mean_live_score,
        "events": [event.event for event in events],
    }


def challenge_sequence_passes(
    challenge: str,
    events: list[MotionEvent],
    *,
    issued_at_ms: int,
    expires_at_ms: int,
) -> bool:
    """Check exact action order and timing from trusted server-side observations.

    This is only the active-challenge policy. It is not liveness/PAD by itself;
    a photo/video replay can still produce apparent motion in some pipelines.
    """
    expected = CHALLENGE_EVENTS.get(challenge)
    if expected is None or len(events) != len(expected):
        return False
    if issued_at_ms < 0 or expires_at_ms <= issued_at_ms:
        return False

    previous = issued_at_ms
    observed: list[str] = []
    for item in events:
        if item.event not in {"turn_left", "turn_right", "blink"}:
            return False
        if item.timestamp_ms <= previous or item.timestamp_ms > expires_at_ms:
            return False
        observed.append(item.event)
        previous = item.timestamp_ms

    return tuple(observed) == expected

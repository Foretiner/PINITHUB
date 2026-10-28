import unittest

from app.liveness import (
    FrameSignal,
    MotionEvent,
    challenge_sequence_passes,
    combine_liveness,
    extract_motion_events,
)


class ChallengePolicyTests(unittest.TestCase):
    def test_accepts_expected_order_within_window(self):
        self.assertTrue(challenge_sequence_passes(
            "turn_left_then_blink",
            [MotionEvent("turn_left", 1_000), MotionEvent("blink", 2_000)],
            issued_at_ms=0,
            expires_at_ms=10_000,
        ))

    def test_rejects_wrong_order_or_wrong_actions(self):
        self.assertFalse(challenge_sequence_passes(
            "turn_left_then_blink",
            [MotionEvent("blink", 1_000), MotionEvent("turn_left", 2_000)],
            issued_at_ms=0,
            expires_at_ms=10_000,
        ))
        self.assertFalse(challenge_sequence_passes(
            "turn_right_then_blink",
            [MotionEvent("turn_left", 1_000), MotionEvent("blink", 2_000)],
            issued_at_ms=0,
            expires_at_ms=10_000,
        ))

    def test_rejects_replayed_or_out_of_window_events(self):
        replayed = [MotionEvent("turn_left", 1_000), MotionEvent("blink", 1_000)]
        expired = [MotionEvent("turn_left", 1_000), MotionEvent("blink", 10_001)]
        self.assertFalse(challenge_sequence_passes("turn_left_then_blink", replayed, issued_at_ms=0, expires_at_ms=10_000))
        self.assertFalse(challenge_sequence_passes("turn_left_then_blink", expired, issued_at_ms=0, expires_at_ms=10_000))

    def test_rejects_unknown_challenge_or_extra_events(self):
        events = [MotionEvent("turn_left", 1_000), MotionEvent("blink", 2_000)]
        self.assertFalse(challenge_sequence_passes("unknown", events, issued_at_ms=0, expires_at_ms=10_000))
        self.assertFalse(challenge_sequence_passes("turn_left_then_blink", events + [MotionEvent("blink", 3_000)], issued_at_ms=0, expires_at_ms=10_000))

    def test_derives_turn_then_blink_from_frame_signals(self):
        signals = [FrameSignal(0.0, 0.05, 0.95) for _ in range(10)]
        signals[4] = FrameSignal(-0.14, 0.05, 0.95)
        signals[5] = FrameSignal(-0.15, 0.05, 0.95)
        signals[7] = FrameSignal(-0.15, 0.85, 0.95)
        signals[8] = FrameSignal(-0.15, 0.10, 0.95)
        self.assertEqual([event.event for event in extract_motion_events(signals)], ["turn_left", "blink"])
        self.assertTrue(combine_liveness("turn_left_then_blink", signals)["livenessPassed"])

    def test_pad_failure_blocks_otherwise_matching_challenge(self):
        signals = [FrameSignal(0.0, 0.05, 0.1) for _ in range(10)]
        signals[4] = FrameSignal(-0.14, 0.05, 0.1)
        signals[7] = FrameSignal(-0.14, 0.85, 0.1)
        signals[8] = FrameSignal(-0.14, 0.10, 0.1)
        result = combine_liveness("turn_left_then_blink", signals)
        self.assertTrue(result["challengePassed"])
        self.assertFalse(result["padPassed"])
        self.assertFalse(result["livenessPassed"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

from audit_core import AuditViolation, check_invariants, seal_event, verify_hash_chain

CAPS = {
    "token_budget": 10,
    "cost_usd": 1.0,
    "wall_clock_ms": 10000,
    "max_retries": 2,
    "max_fanout": 2,
    "reconciliation_ms": 1000,
}

def ev(kind, at, **fields):
    return {
        "event_id": f"id-{kind}-{at}",
        "event_type": kind,
        "timestamp": f"2026-01-01T00:00:{at:02d}Z",
        "correlation_id": "loop-1",
        "issuer_id": "issuer",
        "issuer_type": "system",
        **fields,
    }

def safe_loop():
    return [
        ev("predicate.validated", 1, predicate_id="p1", verdict="valid"),
        ev("check.registered", 2, predicate_id="p1", predicate_type="safety", falsifiable=True),
        ev("loop.start", 3, caps=dict(CAPS)),
    ]

class AuditCoreTests(unittest.TestCase):
    def codes(self, events, as_of=None):
        return {finding["code"] for finding in check_invariants(events, as_of=as_of or datetime(2026, 1, 1, 0, 0, 9, tzinfo=timezone.utc))}

    def test_hash_chain_seals_and_detects_tampering(self):
        first = seal_event(ev("loop.start", 1), None)
        second = seal_event(ev("tool.call", 2, tool_call_id="t1"), first["event_hash"])
        verify_hash_chain([first, second])
        second["tool_call_id"] = "tampered"
        with self.assertRaises(AuditViolation):
            verify_hash_chain([first, second])

    def test_i1_orphan_tool_call_is_detected(self):
        events = safe_loop() + [ev("tool.call", 4, tool_call_id="t1")]
        self.assertIn("I1", self.codes(events))

    def test_i1_duplicate_terminal_is_detected(self):
        events = safe_loop() + [
            ev("tool.call", 4, tool_call_id="t1"),
            ev("tool.result", 5, tool_call_id="t1"),
            ev("circuit_break", 6, tool_call_id="t1", breached_cap="token_budget",
               monitor_attestations=[{"monitor_id":"a","deployment_id":"a","code_lineage":"a"},
                                     {"monitor_id":"b","deployment_id":"b","code_lineage":"b"}]),
        ]
        self.assertIn("I1", self.codes(events))

    def test_m2_registration_without_validation_is_detected(self):
        events = [ev("check.registered", 1, predicate_id="p", predicate_type="safety", falsifiable=True)]
        self.assertIn("M2", self.codes(events))

    def test_i2_loop_without_safety_check_is_detected(self):
        events = [ev("loop.start", 1, caps=dict(CAPS))]
        self.assertIn("I2", self.codes(events))

    def test_i3_idempotency_key_cannot_authorize_two_effects(self):
        events = safe_loop() + [
            ev("tool.result", 4, idempotency_key="key", effect_id="effect-a"),
            ev("tool.result", 5, idempotency_key="key", effect_id="effect-b"),
        ]
        self.assertIn("I3", self.codes(events))

    def test_i4_same_issuer_cannot_verify_model_output(self):
        events = safe_loop() + [
            ev("model.result", 4, output_hash="artifact", issuer_id="same", issuer_type="model",
               lineage_hash="lineage"),
            ev("verify.result", 5, artifact_hash="artifact", issuer_id="same", issuer_type="model",
               lineage_hash="lineage", verify_id="v1", status="pass"),
        ]
        self.assertIn("I4", self.codes(events))

    def test_m3_expired_or_missing_oracle_attestation_is_detected(self):
        events = safe_loop() + [
            ev("verify.result", 4, verify_id="v1", status="pass", oracle_id="oracle-x",
               lineage_hash="lineage"),
        ]
        self.assertIn("M3", self.codes(events))

    def test_m4_single_monitor_circuit_break_is_detected(self):
        events = safe_loop() + [
            ev("circuit_break", 4, breached_cap="token_budget",
               monitor_attestations=[{"monitor_id":"a","deployment_id":"a","code_lineage":"a"}]),
        ]
        self.assertIn("M4", self.codes(events))

    def test_i5_exceeded_token_budget_without_break_is_detected(self):
        events = safe_loop() + [ev("tool.result", 4, token_count=11)]
        self.assertIn("I5", self.codes(events))

    def test_i6_failed_verification_must_be_reconciled(self):
        events = safe_loop() + [
            ev("verify.result", 4, verify_id="v1", status="fail"),
        ]
        as_of = datetime(2026, 1, 1, 0, 0, 7, tzinfo=timezone.utc)
        self.assertIn("I6", self.codes(events, as_of=as_of))

    def test_m5_decayed_rule_cannot_be_cited(self):
        events = safe_loop() + [
            ev("rule.learned", 4, rule_id="r1", source_verify_id="v1",
               half_life_ms=1000, next_revalidation="2026-01-01T00:00:05Z"),
            ev("policy.decision", 8, rule_id="r1", decision="allow"),
        ]
        self.assertIn("M5", self.codes(events))


    def test_i5_break_after_cap_crossing_is_too_late(self):
        events = safe_loop() + [
            ev("tool.result", 4, token_count=11),
            ev("circuit_break", 5, breached_cap="token_budget",
               monitor_attestations=[{"monitor_id":"a","deployment_id":"a","code_lineage":"a"},
                                     {"monitor_id":"b","deployment_id":"b","code_lineage":"b"}]),
        ]
        self.assertIn("I5", self.codes(events))

    def test_predicate_validation_from_another_loop_cannot_authorize_start(self):
        events = [
            ev("predicate.validated", 1, predicate_id="p1", verdict="valid"),
            {**ev("check.registered", 2, predicate_id="p1", predicate_type="safety",
                  falsifiable=True), "correlation_id":"loop-2"},
            {**ev("loop.start", 3, caps=dict(CAPS)), "correlation_id":"loop-2"},
        ]
        self.assertIn("M2", self.codes(events))
        self.assertIn("I2", self.codes(events))

    def test_malformed_cap_value_fails_closed_without_crashing(self):
        caps = dict(CAPS)
        caps["max_retries"] = "unlimited"
        events = [ev("loop.start", 1, caps=caps)]
        self.assertIn("I5", self.codes(events))


    def test_cli_verifies_sealed_jsonl_event_file(self):
        events = safe_loop() + [ev("loop.terminate", 9)]
        sealed = []
        previous = None
        for event in events:
            item = seal_event(event, previous)
            sealed.append(item)
            previous = item["event_hash"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "events.jsonl"
            path.write_text("".join(json.dumps(item) + "\n" for item in sealed), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parents[1] / "scripts/audit_events.py"),
                 str(path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('"status": "PASS"', result.stdout)

    def test_i5_silent_loop_exceeding_wall_clock_is_detected(self):
        as_of = datetime(2026, 1, 1, 0, 0, 14, tzinfo=timezone.utc)
        self.assertIn("I5", self.codes(safe_loop(), as_of=as_of))

    def test_i6_termination_does_not_replace_required_reconciliation(self):
        events = safe_loop() + [
            ev("verify.result", 4, verify_id="v1", status="fail"),
            ev("loop.terminate", 5),
        ]
        as_of = datetime(2026, 1, 1, 0, 0, 7, tzinfo=timezone.utc)
        self.assertIn("I6", self.codes(events, as_of=as_of))
    def test_valid_minimal_safety_loop_has_no_findings(self):
        self.assertEqual(check_invariants(safe_loop(), as_of=datetime(2026, 1, 1, 0, 0, 9, tzinfo=timezone.utc)), [])

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Fail-closed, dependency-free coherence checks for the Boy Scouts audit spec.

This validates structural consistency only. It does not claim to execute the
runtime monitors, external timestamping, transparency logging, or oracle protocol.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EVENT_RE = re.compile(r"""(?:event_type\s*=\s*|event_type\s+IN\s*\([^)]*|\b)(['"])([a-z][a-z0-9_.-]+)\1""")
CAP_FIELDS = (
    "token_budget", "cost_usd", "wall_clock_ms", "max_retries",
    "max_fanout", "reconciliation_ms",
)
REQUIRED_EVENTS = {
    "loop.start", "predicate.registered", "predicate.validated",
    "check.registered", "plan.emit", "tool.call", "tool.result",
    "model.call", "model.result", "verify.attempt", "verify.result",
    "retry.scheduled", "rule.learned", "rule.declined", "rule.revalidated",
    "rule.retired", "oracle.attested", "monitor.attested",
    "monitor.disagreement", "circuit_break", "policy.decision",
    "canary.injected", "canary.result", "log.notarized", "loop.terminate",
}
REQUIRED_COMMON = {
    "event_id", "event_type", "timestamp", "correlation_id", "issuer_id",
    "issuer_type", "schema_version", "event_hash", "stratum_id",
}
REQUIRED_PROPERTIES = {
    "tool_call_id", "verify_id", "predicate_id", "output_hash", "artifact_hash",
    "idempotency_key", "breached_cap", "monitor_attestations",
    "disagreement_id", "source_verify_id", "half_life_ms",
    "next_revalidation", "decay_status", "oracle_id", "expires_at",
    "nonce", "expected_verdict", "actual_verdict", "suite_hash",
    "merkle_root", "external_timestamp", "transparency_log_proof", "parent_hash",
    "goal_attestation", "private_trace",
}

def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: cannot read valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: schema root must be an object")
    return value

def documented_events(root: Path) -> set[str]:
    found: set[str] = set()
    for path in sorted(root.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        for match in EVENT_RE.finditer(content):
            candidate = match.group(2)
            if "." in candidate or candidate == "circuit_break":
                found.add(candidate)
        # Event names in prose and tables are also recognized when backticked.
        found.update(re.findall(r"`([a-z][a-z0-9_-]*\.[a-z][a-z0-9_.-]*)`", content))
    return found

def validate(root: Path) -> list[str]:
    errors: list[str] = []
    schema_path = root / "schemas" / "audit_event.v2.json"
    try:
        schema = load_json(schema_path)
    except ValueError as exc:
        return [str(exc)]

    props = schema.get("properties", {})
    event_schema = props.get("event_type", {})
    enum = set(event_schema.get("enum", []))
    missing_events = sorted(REQUIRED_EVENTS - enum)
    if missing_events:
        errors.append("schema missing required event types: " + ", ".join(missing_events))
    missing_common = sorted(REQUIRED_COMMON - set(schema.get("required", [])))
    if missing_common:
        errors.append("schema missing required common fields: " + ", ".join(missing_common))
    missing_props = sorted(REQUIRED_PROPERTIES - set(props))
    if missing_props:
        errors.append("schema missing referenced properties: " + ", ".join(missing_props))

    caps = props.get("caps", {})
    cap_props = caps.get("properties", {}) if isinstance(caps, dict) else {}
    missing_caps = sorted(set(CAP_FIELDS) - set(cap_props))
    if missing_caps:
        errors.append("caps missing fields: " + ", ".join(missing_caps))
    if isinstance(caps, dict):
        required_caps = set(caps.get("required", []))
        if required_caps != set(CAP_FIELDS):
            errors.append("caps.required must contain exactly: " + ", ".join(CAP_FIELDS))
        for name in CAP_FIELDS:
            definition = cap_props.get(name, {})
            if definition.get("type") not in ("integer", "number"):
                errors.append(f"caps.{name} must be numeric and non-null")
            minimum = definition.get("minimum")
            exclusive_minimum = definition.get("exclusiveMinimum")
            has_positive_floor = (
                (isinstance(minimum, (int, float)) and minimum > 0)
                or (isinstance(exclusive_minimum, (int, float)) and exclusive_minimum >= 0)
            )
            if not has_positive_floor:
                errors.append(f"caps.{name} must have a positive minimum")
        if caps.get("additionalProperties") is not False:
            errors.append("caps.additionalProperties must be false")

    if schema.get("additionalProperties") is not False:
        errors.append("event schema additionalProperties must be false")

    for event in documented_events(root):
        if event not in enum:
            errors.append(f"documented event type absent from schema: {event}")

    # Require conditional payload contracts for events whose fields drive invariants.
    conditional_events = {
        "loop.start": {"caps"},
        "tool.call": {"tool_call_id"},
        "tool.result": {"tool_call_id"},
        "circuit_break": {"breached_cap"},
        "check.registered": {"predicate_id", "falsifiable", "predicate_type"},
        "predicate.validated": {"predicate_id", "verdict"},
        "verify.result": {"verify_id", "status"},
        "rule.learned": {"source_verify_id", "half_life_ms", "next_revalidation"},
        "rule.declined": {"source_verify_id"},
        "canary.injected": {"nonce", "expected_verdict", "oracle_id", "suite_hash"},
        "canary.result": {"nonce", "actual_verdict", "oracle_id"},
        "log.notarized": {"merkle_root", "external_timestamp", "transparency_log_proof"},
    }
    conditions = schema.get("allOf", [])
    covered: dict[str, set[str]] = {}
    for item in conditions:
        condition = item.get("if", {}).get("properties", {}).get("event_type", {}).get("const")
        required = item.get("then", {}).get("required", [])
        if condition:
            covered[condition] = set(required)
    for event, required in conditional_events.items():
        absent = sorted(required - covered.get(event, set()))
        if absent:
            errors.append(f"{event} conditional contract missing required fields: {', '.join(absent)}")

    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"Boy Scouts schema coherence: FAIL ({len(errors)} finding(s))", file=sys.stderr)
        return 1
    print("Boy Scouts schema coherence: PASS")
    print("Scope: event vocabulary, common envelope, required caps, payload fields, conditional contracts.")
    print("Not covered: runtime enforcement, cryptographic verification, TSA, transparency-log availability.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

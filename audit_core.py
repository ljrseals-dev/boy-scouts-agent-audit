"""Small, deterministic audit core for event-chain and invariant checks.

This module validates recorded evidence. It is not a sandbox, a cryptographic
TSA client, a public transparency-log client, or an independent oracle.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

CAPS = ("token_budget", "cost_usd", "wall_clock_ms", "max_retries",
        "max_fanout", "reconciliation_ms")

class AuditViolation(ValueError):
    """Raised when an event chain is malformed or tampered with."""

def _canonical(event: dict[str, Any]) -> bytes:
    body = {key: value for key, value in event.items() if key != "event_hash"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")

def seal_event(event: dict[str, Any], previous_hash: str | None = None) -> dict[str, Any]:
    """Return a copy sealed to the previous event hash."""
    sealed = dict(event)
    sealed["previous_hash"] = previous_hash
    sealed.pop("event_hash", None)
    sealed["event_hash"] = hashlib.sha256(_canonical(sealed)).hexdigest()
    return sealed

def verify_hash_chain(events: Iterable[dict[str, Any]]) -> None:
    """Fail closed on a missing, reordered, or modified event."""
    previous = None
    for index, event in enumerate(events):
        if event.get("previous_hash") != previous:
            raise AuditViolation(f"event {index}: previous_hash does not match chain")
        expected = hashlib.sha256(_canonical(event)).hexdigest()
        if event.get("event_hash") != expected:
            raise AuditViolation(f"event {index}: event_hash mismatch")
        previous = event["event_hash"]

def _parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise AuditViolation("timestamp must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuditViolation(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise AuditViolation("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)

def _time(event: dict[str, Any]) -> datetime:
    return _parse_time(event.get("timestamp"))

def _metric(event: dict[str, Any], name: str) -> float:
    value = event.get(name, 0)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise AuditViolation(f"{name} must be a non-negative number")
    return float(value)

def _before(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return _time(left) < _time(right)

def _finding(code: str, event: dict[str, Any], detail: str) -> dict[str, str]:
    return {"code": code, "event_id": str(event.get("event_id", "")), "detail": detail}

def check_invariants(events: Iterable[dict[str, Any]],
                     as_of: datetime | None = None) -> list[dict[str, str]]:
    """Check implemented evidence invariants; returns deterministic findings.

    Implemented: I1, I2, I3, I4, I5, I6, M2, M3, M4, M5.
    Runtime enforcement still belongs in the caller before side effects occur.
    """
    rows = list(events)
    findings: list[dict[str, str]] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in rows:
        if not isinstance(event, dict):
            raise AuditViolation("each event must be an object")
        if not isinstance(event.get("event_type"), str) or not isinstance(event.get("correlation_id"), str):
            raise AuditViolation("event_type and correlation_id must be strings")
        _time(event)
        grouped[str(event["correlation_id"])].append(event)

    # I1: every tool.call has exactly one terminal, with no orphan terminal.
    calls: dict[str, list[dict[str, Any]]] = defaultdict(list)
    terminals: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in rows:
        call_id = event.get("tool_call_id")
        if event["event_type"] == "tool.call":
            if not call_id:
                findings.append(_finding("I1", event, "tool.call is missing tool_call_id"))
            else:
                calls[str(call_id)].append(event)
        if event["event_type"] in {"tool.result", "circuit_break"}:
            if call_id:
                terminals[str(call_id)].append(event)
    for call_id, call_events in calls.items():
        terminal_count = len(terminals.get(call_id, []))
        if terminal_count != 1:
            findings.append(_finding("I1", call_events[0],
                                     f"tool_call_id {call_id} has {terminal_count} terminal events"))
    for call_id, terminal_events in terminals.items():
        if call_id not in calls:
            findings.append(_finding("I1", terminal_events[0],
                                     f"orphan terminal for tool_call_id {call_id}"))

    # M2 and I2: predicate validation must precede check registration and loop start.
    for event in rows:
        if event["event_type"] == "check.registered":
            valid = any(
                candidate["event_type"] == "predicate.validated"
                and candidate.get("predicate_id") == event.get("predicate_id")
                and candidate.get("verdict") == "valid"
                and candidate.get("correlation_id") == event.get("correlation_id")
                and _before(candidate, event)
                for candidate in rows
            )
            if not valid:
                findings.append(_finding("M2", event, "no preceding valid predicate.validation"))
    for event in rows:
        if event["event_type"] != "loop.start":
            continue
        safety_check = any(
            check["event_type"] == "check.registered"
            and check.get("correlation_id") == event.get("correlation_id")
            and check.get("predicate_type") == "safety"
            and check.get("falsifiable") is True
            and _before(check, event)
            and any(
                valid["event_type"] == "predicate.validated"
                and valid.get("predicate_id") == check.get("predicate_id")
                and valid.get("verdict") == "valid"
                and valid.get("correlation_id") == check.get("correlation_id")
                and _before(valid, check)
                for valid in rows
            )
            for check in rows
        )
        if not safety_check:
            findings.append(_finding("I2", event, "loop.start lacks a preceding validated safety check"))
        caps = event.get("caps")
        if not isinstance(caps, dict) or any(
            not isinstance(caps.get(cap), (int, float))
            or isinstance(caps.get(cap), bool) or caps.get(cap) <= 0
            for cap in CAPS
        ):
            findings.append(_finding("I5", event, "loop.start has missing or non-positive resource caps"))

    # I3: an idempotency key may not authorize multiple distinct effects.
    effects: dict[str, set[str]] = defaultdict(set)
    effect_events: dict[str, dict[str, Any]] = {}
    for event in rows:
        key, effect = event.get("idempotency_key"), event.get("effect_id")
        if key and effect and event["event_type"] in {"tool.result", "model.result"}:
            effects[str(key)].add(str(effect))
            effect_events[str(key)] = event
    for key, effect_ids in effects.items():
        if len(effect_ids) > 1:
            findings.append(_finding("I3", effect_events[key],
                                     f"idempotency key {key} produced multiple effects"))

    # I4/M3: verifier must be independent and its oracle attestation current.
    for result in rows:
        if result["event_type"] != "verify.result":
            continue
        artifact = result.get("artifact_hash")
        judged = [model for model in rows if model["event_type"] == "model.result"
                  and artifact and model.get("output_hash") == artifact]
        for model in judged:
            if result.get("issuer_id") == model.get("issuer_id"):
                findings.append(_finding("I4", result, "verifier and model share issuer_id"))
            if (result.get("issuer_type") == "model"
                    and model.get("issuer_type") == "model"
                    and result.get("lineage_hash") == model.get("lineage_hash")):
                findings.append(_finding("I4", result, "verifier and model share model lineage"))
        oracle_id = result.get("oracle_id")
        if oracle_id:
            attested = any(
                item["event_type"] == "oracle.attested"
                and item.get("oracle_id") == oracle_id
                and item.get("lineage_hash") == result.get("lineage_hash")
                and item.get("issuer_type") == "oracle"
                and _before(item, result)
                and item.get("expires_at") is not None
                and _parse_time(item.get("expires_at")) > _time(result)
                for item in rows
            )
            if not attested:
                findings.append(_finding("M3", result, "oracle lacks a current matching attestation"))

    # M4: a circuit break needs two distinct monitor attestations or escalation.
    for event in rows:
        if event["event_type"] != "circuit_break":
            continue
        attestations = event.get("monitor_attestations", [])
        identities = {
            (item.get("monitor_id"), item.get("deployment_id"), item.get("code_lineage"))
            for item in attestations if isinstance(item, dict)
        }
        if len(identities) < 2 and not event.get("disagreement_id"):
            findings.append(_finding("M4", event, "circuit_break lacks two distinct monitor attestations"))

    # I5: identify the first event that crosses each cap. A later break is too late.
    for correlation, group in grouped.items():
        starts = [e for e in group if e["event_type"] == "loop.start"]
        if not starts:
            continue
        loop = min(starts, key=_time)
        caps = loop.get("caps")
        if not isinstance(caps, dict) or any(cap not in caps for cap in CAPS):
            continue
        scoped = [e for e in group if _time(e) >= _time(loop)]
        breaks = [e for e in scoped if e["event_type"] == "circuit_break"]
        crossings: dict[str, dict[str, Any]] = {}

        token_total = 0.0
        cost_total = 0.0
        retry_total = 0
        for event in sorted(scoped, key=_time):
            token_total += _metric(event, "token_count")
            cost_total += _metric(event, "cost_usd")
            if token_total > caps["token_budget"] and "token_budget" not in crossings:
                crossings["token_budget"] = event
            if cost_total > caps["cost_usd"] and "cost_usd" not in crossings:
                crossings["cost_usd"] = event
            if event["event_type"] == "retry.scheduled":
                retry_total += 1
                if retry_total > caps["max_retries"] and "max_retries" not in crossings:
                    crossings["max_retries"] = event
            if _metric(event, "fanout") > caps["max_fanout"] and "max_fanout" not in crossings:
                crossings["max_fanout"] = event
            elapsed = (_time(event) - _time(loop)).total_seconds() * 1000
            if elapsed > caps["wall_clock_ms"] and "wall_clock_ms" not in crossings:
                crossings["wall_clock_ms"] = event

        for cap, crossing in crossings.items():
            protected = any(
                event.get("breached_cap") == cap and _time(event) <= _time(crossing)
                for event in breaks
            )
            if not protected:
                findings.append(_finding(
                    "I5", crossing,
                    f"{cap} crossed its cap without a prior or concurrent circuit_break"
                ))

    # I6: every failed verification is reconciled by a rule or loop termination
    # before the reconciliation deadline (or as_of, if still running).
    instant = as_of or datetime.now(timezone.utc)
    for result in rows:
        if result["event_type"] != "verify.result" or result.get("status") != "fail":
            continue
        loop = next((e for e in grouped[str(result["correlation_id"])]
                     if e["event_type"] == "loop.start"), None)
        if not loop or not isinstance(loop.get("caps"), dict):
            continue
        deadline = _time(result).timestamp() + loop["caps"].get("reconciliation_ms", 0) / 1000
        reconciled = any(
            e["event_type"] in {"rule.learned", "rule.declined"}
            and e.get("source_verify_id") == result.get("verify_id")
            and e.get("correlation_id") == result.get("correlation_id")
            and _time(e).timestamp() <= deadline
            for e in rows
        )
        terminated = any(e["event_type"] == "loop.terminate"
                         and e.get("correlation_id") == result.get("correlation_id")
                         and _time(e).timestamp() <= deadline for e in rows)
        if not reconciled and not terminated and instant.timestamp() > deadline:
            findings.append(_finding("I6", result, "failed verification missed reconciliation deadline"))

    # M5: active policy decisions cannot cite a rule beyond twice its half-life.
    learned = {e.get("rule_id"): e for e in rows if e["event_type"] == "rule.learned" and e.get("rule_id")}
    for decision in rows:
        rule_id = decision.get("rule_id")
        if decision["event_type"] != "policy.decision" or not rule_id:
            continue
        rule = learned.get(rule_id)
        if not rule or not isinstance(rule.get("half_life_ms"), (int, float)):
            findings.append(_finding("M5", decision, "cited rule has no valid learned record"))
            continue
        age_ms = (_time(decision) - _time(rule)).total_seconds() * 1000
        revalidated = any(e["event_type"] == "rule.revalidated"
                          and e.get("rule_id") == rule_id and _before(rule, e)
                          and _before(e, decision) for e in rows)
        if rule["half_life_ms"] <= 0:
            findings.append(_finding("M5", decision, "cited rule has non-positive half-life"))
        elif age_ms > 2 * rule["half_life_ms"] and not revalidated:
            findings.append(_finding("M5", decision, "cited rule exceeded twice its half-life"))

    return findings

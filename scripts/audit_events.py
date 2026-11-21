#!/usr/bin/env python3
"""Verify a JSONL audit event chain and evaluate implemented invariants."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit_core import AuditViolation, check_invariants, verify_hash_chain  # noqa: E402

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path, help="JSON Lines event file")
    parser.add_argument("--as-of", help="ISO-8601 time for deadline checks; defaults to current UTC")
    parser.add_argument("--skip-chain", action="store_true",
                        help="Skip hash-chain verification (not recommended)")
    args = parser.parse_args()
    try:
        rows = []
        with args.events.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AuditViolation(f"line {line_number}: invalid JSON: {exc}") from exc
                if not isinstance(value, dict):
                    raise AuditViolation(f"line {line_number}: event must be a JSON object")
                rows.append(value)
        if not args.skip_chain:
            verify_hash_chain(rows)
        as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else None
        findings = check_invariants(rows, as_of=as_of)
    except (OSError, AuditViolation, ValueError) as exc:
        print(f"AUDIT INPUT ERROR: {exc}", file=sys.stderr)
        return 2
    if findings:
        print(json.dumps({"status": "FAIL", "finding_count": len(findings),
                          "findings": findings}, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "events_checked": len(rows),
                      "chain_verified": not args.skip_chain}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

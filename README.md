# Boy Scouts Loop Audit System — Specification v2.0

This repository contains the v2.0 audit doctrine plus an executable evidence-checking core.

## Doctrine and specifications
- [Governing doctrine](DOCTRINE.md)
- [Defect closure register](DEFECT_CLOSURE.md)
- [Invariants](INVARIANTS.md)
- [Canary suite specification](CANARY_SUITE.md)
- [Dual-monitor specification](DUAL_MONITOR.md)
- [Trust-anchor specification](TRUST_ANCHOR.md)
- [Acceptance scenario matrix](ACCEPTANCE_TESTS_v2.md)
- [Carbon-Dating Changelog](CDC.md)
- [Roadmap](ROADMAP.md)
- [Self-audit](SELF_AUDIT_v2.md)

## Executable checks

Python 3.10+; no third-party packages required.

```sh
python scripts/check_schema_coherence.py
PYTHONPATH=scripts python -m unittest discover -s tests -v
python scripts/audit_events.py path/to/events.jsonl
```

The schema gate checks documented event vocabulary, common envelope fields, bounded non-null caps, event payload properties, and selected conditional requirements.

The event verifier checks a SHA-256 hash chain and the implemented evidence invariants I1–I6 and M2–M5. It returns findings and exits non-zero on violations. It is an offline verifier over supplied JSONL evidence; it is not itself a runtime policy-enforcement point.

## Explicit coverage boundary

The current executable core does **not** provide a production append-only ledger, pre-side-effect enforcement adapter, independent falsifiability analyzer, hidden rotating canary service, independent oracle deployment/attestation, dual-monitor supervisor, RFC 3161 client, public transparency-log publisher/verifier, or external key custody. The CLI cannot prove that an event source is truthful or complete. Those controls remain open until implemented with independently operated services and tests.

The acceptance matrix labels non-executable runtime scenarios as open. A passing local or CI check must not be used to claim that every D1–D14 or R1–R11 roadmap item is closed.

## CI

GitHub Actions runs schema coherence and the unit/negative test suite on pushes and pull requests.

## License
MIT.

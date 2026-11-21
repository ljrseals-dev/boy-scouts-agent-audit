# Boy Scouts Loop Audit System — Specification v2.0

This repository contains the v2.0 audit doctrine and an executable **schema-coherence gate**. The gate is intentionally narrower than the full runtime protocol: it checks that documented event vocabulary, event envelope fields, required bounded caps, and selected event-specific payload contracts agree with the JSON Schema.

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

Run locally with Python 3.10+ and no third-party packages:

```sh
python scripts/check_schema_coherence.py
PYTHONPATH=scripts python -m unittest discover -s tests -v
```

GitHub Actions runs these commands on pushes and pull requests. The negative tests verify that a phantom documented event and a nullable/unbounded cap are rejected.

## Explicit coverage boundary

A passing schema-coherence check does **not** prove runtime enforcement of I1–I6 or M1–M5. This repository does not yet provide production implementations of the hidden canary service, independent falsifiability analyzer, dual-monitor supervisor, append-only event ledger, RFC 3161 client, transparency-log publisher/verifier, or wall-clock circuit breaker. Those are separate roadmap deliverables and must not be represented as implemented merely because their specifications exist.

## License
MIT.

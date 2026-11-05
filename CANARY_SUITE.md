# Canary Suite Specification (closes D4)

## Properties
- **Hidden**: suite contents are not visible to the oracle under test.
- **Rotating**: new canaries drawn on a cadence (default: every 24 h or every N verifications).
- **Unannounced**: injection occurs without prior signal to the oracle.
- **Nonce-tagged**: every injection carries a unique nonce recorded in canary.injected.
- **Poison-resistant**: canaries are generated from a separate, higher-assurance source; oracle cannot influence future canary generation.

## Events
- canary.injected (nonce, expected_verdict, oracle_id, suite_hash)
- canary.result (nonce, actual_verdict, oracle_id)

## Pass Criterion (makes D4 testable)
Over a rolling window of K injections (K ≥ 50):
- Detection rate (actual_verdict matches expected on known-fail canaries) ≥ θ (default θ = 0.95)
- False-pass rate on known-fail ≤ 1 − θ
- No systematic miss of an entire canary family

Failure of the pass criterion → oracle.attested is revoked; subsequent verify.result from that oracle are rejected (M3).

## Poison Resistance
Canary generation key material is held by the dual-monitor system and never exposed to any oracle. Rotation uses a forward-secure ratchet.
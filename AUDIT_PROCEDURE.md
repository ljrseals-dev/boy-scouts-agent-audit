# Audit Procedure

A numbered, repeatable procedure an operator (or automated auditor) runs for every logical loop.

## Pre-flight (before loop.start is accepted)

1. Confirm at least one check.registered exists for the correlation_id with falsifiable = true.
2. Confirm a safety-class check is present (or deployment policy equivalent).
3. Confirm caps object is fully populated (token_budget, cost_usd, wall_clock_ms, max_retries, max_fanout, verify_ms) according to policy.
4. Confirm oracle_id is assigned and is independent of any generator model_family that will be used.
5. Confirm environment_hash is captured and matches the expected environment.
6. Confirm goal_hash is recorded and matches the human-intended goal (or has explicit human sign-off).
7. Reject the loop.start if any of the above fail. Do not proceed.

## In-flight (continuous monitors)

8. On every tool.call: assert I3 (idempotency_key present if side_effecting) and auth_context present.
9. On every tool.result or model.result: assert schema validation against expected schema_hash.
10. On every verify.attempt / verify.result: assert I4 (issuer independence).
11. Continuously evaluate cumulative tokens, cost, wall-clock, retries, fan-out against caps (I5). Emit circuit_break on breach.
12. Assert no check.registered appears after the first side-effecting event (I2 extension).
13. Assert every tool.call receives exactly one terminal event (I1) within the verify_ms / wall_clock bound.
14. Propagate correlation_id and maintain hash chain (previous_hash).

## Post-flight (after loop.terminate or circuit_break)

15. Reconcile the failure ledger: every verify.result:fail must have a rule.learned or rule.declined (I6). Block or flag if missing.
16. Extract and persist any new rules into the agent playbook.
17. Emit final cost_summary (tokens, cost_usd, latency, retry count, fan-out peak).
18. Verify the hash chain integrity from loop.start to terminal event.
19. Archive the correlation_id stream according to retention policy.
20. If any S0/S1 finding occurred, escalate to human review with the full minimal failing context.

## Failure-Only Feedback Contract

When a retry is scheduled:
- The retry.scheduled event MUST carry only the minimal failing diff (the specific assertion that failed + the minimal surrounding context required to understand it).
- Full original context is forbidden unless explicitly justified and size-capped.
- This reduces cost, limits context pollution, and forces the generator to focus on the actual defect.
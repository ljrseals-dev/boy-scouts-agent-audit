# Corrected Audit Procedure v2.0 (strictly schema-bound)

## Pre-flight (before loop.start accepted)
1. Confirm predicate.registered + predicate.validated (verdict=valid) for at least one safety predicate.
2. Confirm check.registered references the validated predicate and falsifiable=true.
3. Confirm goal_attestation (signed) is present OR Intent Verification Oracle has emitted a policy.decision=allow for the goal_hash (D10 resolved).
4. Confirm all caps are non-null and satisfy schema minima (null caps = schema violation).
5. Confirm oracle_id has a current oracle.attested (non-expired, matching lineage).
6. Confirm dual monitors are registered and attested.
7. Confirm environment_hash matches expected.
8. Reject loop.start on any failure. No partial start.

## In-flight
9. On every tool.call: enforce I3 (idempotency_key if side_effecting), auth_context, expected_schema_hash.
10. On every tool.result / model.result: schema validation; cost/latency recording.
11. On every verify.attempt: assert private_trace_present=false; oracle must be attested (M3).
12. On every verify.result: enforce I4 three-clause independence; record evidence.
13. Dual monitors continuously evaluate all six caps (I5); emit monitor.attested; require agreement for circuit_break (M4).
14. Enforce no late check.registered after first side-effecting event.
15. Enforce I1 (exactly one terminal per tool.call) within bounds.
16. Maintain hash chain; at stratum boundaries emit log.notarized.

## Post-flight
17. Within caps.reconciliation_ms (I6 bounded): every verify.result:fail must have rule.learned or rule.declined.
18. For every rule.learned: set half_life_ms and next_revalidation (M5).
19. Emit cost_summary on loop.terminate; set reconciliation_complete=true only when I6 is satisfied.
20. Verify hash-chain integrity and presence of required log.notarized events.
21. Archive according to retention; escalate any S0/S1 findings.

## Failure-Only Feedback Contract (context-pollution safe)
- retry.scheduled.minimal_diff is size-capped, injection-scanned, and free of executable content.
- Diff envelope contains only: failing assertion identifier, minimal surrounding structured data, and a hash of the larger context (not the context itself).
- Full original context is never re-injected unless an explicit, audited policy.decision allows it under a separate budget.
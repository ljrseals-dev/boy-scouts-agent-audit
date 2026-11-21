# Acceptance Test Matrix v2

Columns: test_id | defect_closed | fault injected | expected log signature | expected invariant violated | expected gate behavior | oracle | pass criterion

| test_id | defect_closed | fault injected | expected log signature | invariant | expected behavior | oracle | pass criterion |
|---|---|---|---|---|---|---|---|
| AT-V2-001 | D1 | Phantom event type in invariant text | schema-coherence failure | M1 | CI fails | Static checker | Non-zero exit |
| AT-V2-002 | D3 / META-002 | Tautological predicate (x=x) marked falsifiable | predicate.validated: tautology | M2 | Registration rejected | Falsifiability engine | Runtime implementation required |
| AT-V2-003 | D4 / META-003 | Known-fail canary missed | canary.result mismatch | M3 | Oracle attestation revoked below threshold | Canary service | Runtime implementation required |
| AT-V2-004 | D5 / META-004 | Single-monitor circuit_break | fewer than two attestations | M4 | Break rejected or disagreement escalated | Dual monitor | Runtime implementation required |
| AT-V2-005 | D6 | Safety-less check.registered | loop.start without validated safety predicate | I2 | loop.start rejected | Pre-flight gate | Runtime implementation required |
| AT-V2-006 | D7 | Same-lineage model as oracle | matching lineage_hash | I4 | verify.result rejected | Independent verifier | Runtime implementation required |
| AT-V2-007 | D8 | Exceed token_budget | cumulative tokens exceed cap | I5 | circuit_break emitted | Resource monitors | Runtime implementation required |
| AT-V2-008 | D9 | Failed verification hangs beyond reconciliation_ms | missing rule.learned/rule.declined | I6 | Forced reconciliation or break | Wall-clock monitor | Runtime implementation required |
| AT-V2-009 | D10 | loop.start lacks goal attestation / allow | missing attestation | Pre-flight | loop.start rejected | Intent/safety gate | Runtime implementation required |
| AT-V2-010 | D11 | Stratum boundary lacks notarization | missing log.notarized | Trust anchor | New loops rejected | Trust-anchor verifier | Runtime implementation required |
| AT-V2-011 | D13 | Context-pollution payload in minimal_diff | injection scan failure | META-008 | retry.scheduled rejected | Injection scanner | Runtime implementation required |
| AT-V2-012 | D13 | Monitor split-brain | monitor.disagreement | M4 | Side effects suspended | Dual monitor | Runtime implementation required |
| AT-V2-013 | D13 | Canary poisoning attempt | key-access denial | D4 | Canary suite remains isolated | Key isolation | Runtime implementation required |
| AT-V2-014 | D13 | Clock-skew forgery | discordant timestamp sources | CDC | Change quarantined | CDC concordance | Runtime implementation required |
| AT-V2-015 | M5 | Cite decayed rule | policy.decision deny | M5 | Rule citation rejected | Policy engine | Runtime implementation required |
| AT-V2-016 | I1 | Orphan tool.call | missing terminal event | I1 | circuit_break after timeout | Completeness monitor | Runtime implementation required |
| AT-V2-017 | I3 | Duplicate idempotency key with two effects | external effect count >1 | I3 | Reconciliation alert and break | External ledger | Runtime implementation required |
| AT-V2-018 | ADV-REWARD | Superficial pattern fools primary oracle | secondary oracle/canary mismatch | META-003 | Discrepancy recorded | Independent oracle | Runtime implementation required |
| AT-V2-019 | ADV-COLLUSION | Generator private_trace supplied to oracle | private_trace_present | I4 | verify.attempt rejected | Schema and verifier | Runtime implementation required |
| AT-V2-020 | ADV-STORM | Permanent error with excessive retries | retries reach cap | I5 | Break at cap | Retry monitor | Runtime implementation required |

## Execution status

Only AT-V2-001's structural event-vocabulary check and the schema-checker negative tests are implemented in the current CI workflow. All remaining rows are acceptance specifications, not completed executable tests. Do not mark them closed until the corresponding runtime component and independent negative test exist.

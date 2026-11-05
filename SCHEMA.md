# Corrected Event Schema v2.0

## Design Rules
- Append-only, immutable (mutability = none for all fields after emission).
- Null caps are a schema violation (caps fields are non-nullable integers/numbers with explicit minimums).
- Every event carries the common envelope.
- Retention: default 365 days; S0/S1-related streams 7 years; hash-chain and notarization proofs retained for the longest related retention.
- External trust anchor required at every stratum boundary (see TRUST_ANCHOR.md).

## Common Envelope (all events)

| Field | Type | Nullable | Description | Invariants Served |
|-------|------|----------|-------------|-------------------|
| event_id | UUID | no | Globally unique | I1, M1 |
| event_type | enum | no | See Event Types | M1 |
| timestamp | RFC3339 ms | no | Emission time (host clock) | CDC |
| correlation_id | UUID | no | Loop-scoped | all |
| parent_event_id | UUID | yes (only loop.start) | Causal parent | M1 |
| issuer_id | string | no | Principal/component | I4, M3, M4 |
| issuer_type | enum(model,tool,orchestrator,human,system,monitor,oracle,analyzer) | no | | I4 |
| schema_version | string | no | "2.0.0" | M1 |
| event_hash | string (SHA-256) | no | Canonical content hash | Leave No Trace |
| previous_hash | string | yes (genesis) | Hash-chain link | Leave No Trace |
| stratum_id | string | no | CDC stratum | CDC |
| lineage_hash | string | yes | Training/model lineage for model/oracle issuers | I4, M3 |

## Event Types (complete)

### loop.start
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| goal_hash | string | no | I2, D10 |
| goal_attestation | object (signed) | no | D10 |
| caps.token_budget | integer ≥0 | no | I5 |
| caps.cost_usd | number ≥0 | no | I5 |
| caps.wall_clock_ms | integer ≥1 | no | I5 |
| caps.max_retries | integer ≥0 | no | I5 |
| caps.max_fanout | integer ≥1 | no | I5 |
| caps.verify_ms | integer ≥1 | no | I5 |
| caps.reconciliation_ms | integer ≥1 | no | I6, D9 |
| oracle_id | string | no | M3 |
| environment_hash | string | no | |
| intent_oracle_id | string | no | D10 |

### predicate.registered
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| predicate_id | UUID | no | M2 |
| predicate | structured | no | M2 |
| predicate_type | enum(safety,correctness,resource,custom) | no | I2 |
| inputs_schema | object | no | |
| pass_criterion | string | no | |
| environment_hash | string | no | |

### predicate.validated
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| predicate_id | UUID | no | M2 |
| analyzer_id | string | no | M2 |
| verdict | enum(valid,tautology,vacuous,unsatisfiable,no_counterexample) | no | M2 |
| counterexample_witness | object | yes | M2 |
| analysis_hash | string | no | |

### check.registered
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| check_id | UUID | no | I2 |
| predicate_id | UUID | no | M2 |
| falsifiable | boolean | no (must be true) | M2 |
| validated_by | UUID (predicate.validated event) | no | M2 |

### plan.emit
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| plan_id | UUID | no | |
| goal_hash | string | no | |
| steps | array | no | |
| resource_estimate | object | no | I5 |
| model_call_id | UUID | yes | |

### tool.call
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| tool_call_id | UUID | no | I1, I3 |
| tool_id | string | no | |
| arguments | object | no | |
| idempotency_key | string | no if side_effecting | I3 |
| side_effecting | boolean | no | I3 |
| irreversible | boolean | no | |
| auth_context | object | no | |
| expected_schema_hash | string | no | |

### tool.result
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| tool_call_id | UUID | no | I1 |
| status | enum(success,failure,timeout,rejected) | no | I1 |
| result | object | yes | |
| cost_usd | number | yes | I5 |
| latency_ms | integer | no | |
| error_class | string | yes | |
| schema_hash | string | no | |

### model.call / model.result
(Standard fields as in v1, plus lineage_hash required on model.result)

### verify.attempt
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| verify_id | UUID | no | I4 |
| check_id | UUID | no | |
| artifact_hash | string | no | |
| oracle_id | string | no | M3 |
| input_context_hash | string | no | |
| private_trace_present | boolean | no (must be false) | I4 |

### verify.result
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| verify_id | UUID | no | I4, I6 |
| status | enum(pass,fail,error) | no | I6 |
| evidence | object | yes | |
| issuer_id | string | no | I4 |
| issuer_type | enum | no | I4 |
| oracle_attestation_id | UUID | no | M3 |
| lineage_hash | string | no | I4 |

### retry.scheduled
(As v1 + minimal_diff must be injection-scanned and size-capped)

### rule.learned
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| rule_id | UUID | no | I6, M5 |
| source_verify_id | UUID | no | I6 |
| rule_text | string | no | |
| scope | string | no | |
| half_life_ms | integer | no | M5 |
| next_revalidation | RFC3339 | no | M5 |
| decay_status | enum(active,pending_revalidation,decayed) | no | M5 |

### rule.declined
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| source_verify_id | UUID | no | I6 |
| justification | string | no (min length policy) | I6 |
| declined_by | string | no | |

### rule.revalidated / rule.retired
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| rule_id | UUID | no | M5 |
| evidence | object | no | M5 |
| new_half_life_ms | integer | yes | M5 |

### oracle.attested
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| oracle_id | string | no | M3 |
| lineage_hash | string | no | M3 |
| attestation_expiry | RFC3339 | no | M3 |
| canary_suite_hash | string | no | D4 |

### monitor.attested
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| monitor_id | string | no | M4 |
| observed_cap | string | no | M4 |
| observed_value | number | no | M4 |
| attestation_hash | string | no | M4 |

### monitor.disagreement
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| monitors | array | no | M4 |
| values | object | no | M4 |
| escalation_id | UUID | no | M4 |

### circuit_break
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| reason | string | no | I5, M4 |
| breached_cap | string | yes | I5 |
| triggering_event_id | UUID | no | |
| monitor_attestations | array (≥2) | no | M4 |
| disagreement_id | UUID | yes | M4 |

### policy.decision
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| policy_id | string | no | |
| decision | enum(allow,deny,escalate) | no | |
| evidence | object | no | |

### canary.injected / canary.result
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| canary_id | UUID | no | D4 |
| nonce | string | no | D4 |
| expected_verdict | enum | no | D4 |
| actual_verdict | enum | yes (result) | D4 |
| oracle_id | string | no | D4 |

### log.notarized
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| merkle_root | string | no | D11 |
| external_timestamp | RFC3161 | no | D11 |
| transparency_log_proof | object | no | D11 |
| stratum_id | string | no | CDC |

### loop.terminate
| Field | Type | Nullable | Invariants |
|-------|------|----------|------------|
| status | enum(success,failure,circuit_break,cancelled) | no | |
| cost_summary | object | no | |
| open_checks | array | no | |
| final_artifact_hash | string | yes | |
| reconciliation_complete | boolean | no | I6 |

## JSON Schema Fragment
See `schemas/audit_event.v2.json` (machine-readable, used by M1 cross-reference checker).

## Coherence Assertion (M1)
Zero orphan events: every event_type referenced in any invariant appears in the schema enum.  
Zero orphan fields: every field referenced in any detection query appears in the corresponding event definition.  
Automated check: `scripts/check_schema_coherence.py` (or equivalent) must pass before any stratum is accepted.
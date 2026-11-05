# Loop Audit Log Specification

## Design Principles
- Append-only, durable, tamper-evident.
- Every event is immutable after emission (mutability = none).
- Content-addressable where practical (event_hash).
- Retention: configurable per deployment; minimum 90 days for S0/S1 related events; default 1 year recommended.
- All timestamps are UTC, RFC 3339 with millisecond precision.
- Correlation via `correlation_id` (loop-scoped) and `parent_event_id` (causal).

## Common Envelope (all events)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | UUID | yes | Globally unique |
| event_type | string (enum) | yes | One of the types below |
| timestamp | RFC3339 | yes | Emission time |
| correlation_id | UUID | yes | Shared across the entire logical loop |
| parent_event_id | UUID \| null | yes | Causal parent; null only for loop.start |
| issuer_id | string | yes | Principal or component that emitted the event |
| issuer_type | enum(model, tool, orchestrator, human, system) | yes | |
| schema_version | string | yes | e.g. "1.0.0" |
| event_hash | string | yes | SHA-256 of canonical serialization of the rest of the event |
| previous_hash | string \| null | yes | Hash of prior event in the stream (hash chain) |

## Event Types and Required Fields

### loop.start
| Field | Type | Required |
|-------|------|----------|
| goal_hash | string | yes |
| caps | object | yes |
| caps.token_budget | integer \| null | yes |
| caps.cost_usd | number \| null | yes |
| caps.wall_clock_ms | integer \| null | yes |
| caps.max_retries | integer | yes |
| caps.max_fanout | integer | yes |
| caps.verify_ms | integer \| null | yes |
| oracle_id | string | yes |
| environment_hash | string | yes |

### check.registered
| Field | Type | Required |
|-------|------|----------|
| check_id | UUID | yes |
| predicate | string or structured | yes |
| predicate_type | enum(safety, correctness, resource, custom) | yes |
| falsifiable | boolean | yes (must be true) |
| inputs_schema | object | yes |
| pass_criterion | string | yes |
| environment_hash | string | yes |

### plan.emit
| Field | Type | Required |
|-------|------|----------|
| plan_id | UUID | yes |
| goal_hash | string | yes |
| steps | array | yes |
| resource_estimate | object | yes |
| model_call_id | UUID \| null | yes |

### tool.call
| Field | Type | Required |
|-------|------|----------|
| tool_call_id | UUID | yes |
| tool_id | string | yes |
| arguments | object | yes |
| idempotency_key | string \| null | yes (required if side_effecting) |
| side_effecting | boolean | yes |
| irreversible | boolean | yes |
| auth_context | object | yes |
| expected_schema_hash | string | yes |

### tool.result
| Field | Type | Required |
|-------|------|----------|
| tool_call_id | UUID | yes |
| status | enum(success, failure, timeout, rejected) | yes |
| result | object \| null | yes |
| cost_usd | number \| null | yes |
| latency_ms | integer | yes |
| error_class | string \| null | yes |
| schema_hash | string | yes |

### model.call
| Field | Type | Required |
|-------|------|----------|
| model_call_id | UUID | yes |
| model_id | string | yes |
| model_family | string | yes |
| prompt_hash | string | yes |
| temperature | number \| null | yes |
| seed | integer \| null | yes |
| max_tokens | integer \| null | yes |

### model.result
| Field | Type | Required |
|-------|------|----------|
| model_call_id | UUID | yes |
| status | enum(success, failure, truncated) | yes |
| output_hash | string | yes |
| token_usage | object | yes |
| latency_ms | integer | yes |

### verify.attempt
| Field | Type | Required |
|-------|------|----------|
| verify_id | UUID | yes |
| check_id | UUID | yes |
| artifact_hash | string | yes |
| oracle_id | string | yes |
| input_context_hash | string | yes |

### verify.result
| Field | Type | Required |
|-------|------|----------|
| verify_id | UUID | yes |
| status | enum(pass, fail, error) | yes |
| evidence | object \| null | yes |
| issuer_id | string | yes |
| issuer_type | enum | yes |

### retry.scheduled
| Field | Type | Required |
|-------|------|----------|
| retry_id | UUID | yes |
| original_event_id | UUID | yes |
| attempt | integer | yes |
| delay_ms | integer | yes |
| reason | string | yes |
| minimal_diff | object | yes |
| context_size_tokens | integer | yes |

### rule.learned
| Field | Type | Required |
|-------|------|----------|
| rule_id | UUID | yes |
| source_verify_id | UUID | yes |
| rule_text | string | yes |
| scope | string | yes |

### rule.declined
| Field | Type | Required |
|-------|------|----------|
| source_verify_id | UUID | yes |
| justification | string | yes |
| declined_by | string | yes |

### circuit_break
| Field | Type | Required |
|-------|------|----------|
| reason | string | yes |
| breached_cap | string \| null | yes |
| triggering_event_id | UUID | yes |

### loop.terminate
| Field | Type | Required |
|-------|------|----------|
| status | enum(success, failure, circuit_break, cancelled) | yes |
| cost_summary | object | yes |
| open_checks | array | yes |
| final_artifact_hash | string \| null | yes |

## Retention
- Default: 365 days.
- S0/S1 related events (any event in a loop that produced an S0/S1 finding): 7 years or legal minimum.
- Hash chain must be preserved for the retention window.
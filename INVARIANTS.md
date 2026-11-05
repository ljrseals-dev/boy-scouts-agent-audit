# Formal Invariants I1–I6

Each invariant is stated with a machine-checkable assertion, failure mode, detection query (over the append-only log), and remediation.

## I1 Completeness
**Assertion**  
∀ tool.call e ∃ exactly one terminal event t where  
(t.event_type ∈ {tool.result, circuit_break} ∧ t.tool_call_id = e.tool_call_id)  
and no second terminal event for the same tool_call_id.

**Failure mode**  
Orphaned tool.call (hang) or duplicate terminal results (double-spend / double-apply).

**Detection query**  
```
SELECT tool_call_id, COUNT(*) AS terminals
FROM events
WHERE event_type IN ('tool.result', 'circuit_break')
GROUP BY tool_call_id
HAVING terminals != 1
UNION
SELECT c.tool_call_id, 0
FROM events c
WHERE c.event_type = 'tool.call'
  AND NOT EXISTS (
    SELECT 1 FROM events t
    WHERE t.tool_call_id = c.tool_call_id
      AND t.event_type IN ('tool.result', 'circuit_break')
  );
```

**Remediation**  
On detection: emit circuit_break for the correlation_id, mark the tool.call as failed, and surface to operator. Prevent further acts until resolved.

## I2 Pre-registration
**Assertion**  
∀ loop.start s ∃ check.registered r where  
r.timestamp < s.timestamp  
∧ r.correlation_id = s.correlation_id  
∧ r.falsifiable = true  
∧ at least one r.predicate_type = 'safety' (or deployment policy equivalent).

No side-effecting tool.call or model.call may precede the first check.registered for that correlation_id.

**Failure mode**  
Loop executes without a falsifiable definition of done → "looks good" termination becomes possible.

**Detection query**  
```
SELECT s.event_id
FROM events s
WHERE s.event_type = 'loop.start'
  AND NOT EXISTS (
    SELECT 1 FROM events r
    WHERE r.event_type = 'check.registered'
      AND r.correlation_id = s.correlation_id
      AND r.timestamp < s.timestamp
      AND r.falsifiable = true
  );
```

**Remediation**  
Reject loop.start at the gate. If already started, immediate circuit_break.

## I3 Idempotency
**Assertion**  
∀ tool.call e where e.side_effecting = true  
→ e.idempotency_key IS NOT NULL  
∧ (∀ e1, e2 with same idempotency_key → external effect cardinality ≤ 1).

**Failure mode**  
Replay or crash recovery produces duplicate external effects (double charge, double write).

**Detection query**  
```
SELECT idempotency_key, COUNT(DISTINCT tool_call_id) AS calls
FROM events
WHERE event_type = 'tool.call' AND side_effecting = true
GROUP BY idempotency_key
HAVING calls > 1;
-- Plus external reconciliation: effect count per key must be ≤ 1
```

**Remediation**  
Tool adapters must treat duplicate keys as no-ops and return the original result. On detection of multiple effects, circuit_break and alert for manual reconciliation.

## I4 Independence
**Assertion**  
∀ verify.result v that references a model.result m (via artifact or verify.attempt)  
→ v.issuer_id ≠ m.issuer_id  
∧ v.issuer_type ≠ 'model' OR v.model_family ≠ m.model_family  
(strong form: oracle must be different model family or non-model).

**Failure mode**  
Generator grades itself → confirmation bias, reward hacking, undetected errors.

**Detection query**  
```
SELECT v.event_id
FROM events v
JOIN events a ON a.event_id = v.parent_event_id OR a.verify_id = v.verify_id
JOIN events m ON m.event_type = 'model.result' AND m.output_hash = a.artifact_hash
WHERE v.event_type = 'verify.result'
  AND v.issuer_id = m.issuer_id;
```

**Remediation**  
Reject the verify.result, force re-verification by an independent issuer, or circuit_break.

## I5 Boundedness
**Assertion**  
∀ loop.start s  
→ s.caps is fully populated for the deployment policy  
∧ no cumulative metric (tokens, cost_usd, wall_clock_ms, fanout, retries) exceeds the declared cap without a preceding or concurrent circuit_break.

**Failure mode**  
Resource exhaustion, runaway cost, indefinite hang.

**Detection query**  
```
-- Example for tokens (similar for others)
SELECT s.correlation_id
FROM events s
WHERE s.event_type = 'loop.start'
  AND (
    (SELECT COALESCE(SUM(token_usage.total),0) FROM events m
     WHERE m.correlation_id = s.correlation_id AND m.event_type = 'model.result')
    > s.caps.token_budget
  )
  AND NOT EXISTS (
    SELECT 1 FROM events c
    WHERE c.correlation_id = s.correlation_id
      AND c.event_type = 'circuit_break'
      AND c.breached_cap = 'token_budget'
  );
```

**Remediation**  
Independent monitor emits circuit_break on breach. Caps are hard; soft warnings are insufficient.

## I6 Rule Persistence
**Assertion**  
∀ verify.result v where v.status = 'fail'  
→ eventually ∃ rule.learned r with r.source_verify_id = v.verify_id  
OR ∃ rule.declined d with d.source_verify_id = v.verify_id ∧ d.justification IS NOT NULL.

"Eventually" is bounded by loop.terminate or a configurable max delay.

**Failure mode**  
Failures are forgotten; the same defect recurs indefinitely (violates Do a Good Turn Daily).

**Detection query**  
```
SELECT v.event_id
FROM events v
WHERE v.event_type = 'verify.result' AND v.status = 'fail'
  AND NOT EXISTS (
    SELECT 1 FROM events r
    WHERE r.event_type IN ('rule.learned', 'rule.declined')
      AND r.source_verify_id = v.verify_id
  )
  AND EXISTS (
    SELECT 1 FROM events t
    WHERE t.event_type = 'loop.terminate'
      AND t.correlation_id = v.correlation_id
  );
```

**Remediation**  
Block loop.terminate until every failing verify.result has a corresponding rule.learned or rule.declined. Surface outstanding failures to operator.
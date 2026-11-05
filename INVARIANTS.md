# Invariants I1–I6 + Meta-Invariants M1–M5 (v2.0)

All queries use a consistent SQL dialect over the append-only event log.  
Every invariant includes a negative test that proves the detection query fires.

## I1 Completeness
**Assertion**  
∀ tool.call e ∃ exactly one terminal t ∈ {tool.result, circuit_break} with matching tool_call_id, and no second terminal.

**Detection Query**
```sql
SELECT tool_call_id FROM (
  SELECT tool_call_id, COUNT(*) AS n
  FROM events
  WHERE event_type IN ('tool.result','circuit_break')
  GROUP BY tool_call_id
) WHERE n != 1
UNION
SELECT c.tool_call_id
FROM events c
WHERE c.event_type = 'tool.call'
  AND NOT EXISTS (
    SELECT 1 FROM events t
    WHERE t.tool_call_id = c.tool_call_id
      AND t.event_type IN ('tool.result','circuit_break')
  );
```

**Failure mode** Orphaned call or double-apply.  
**Blast radius** Data / money (duplicate side-effects).  
**Remediation** Emit circuit_break; mark call failed; block further acts.  
**Negative test** Inject tool.call with no terminal after timeout → query returns the id; circuit_break emitted.

## I2 Pre-registration (corrected)
**Assertion**  
∀ loop.start s ∃ check.registered r  
  WHERE r.timestamp < s.timestamp  
  AND r.correlation_id = s.correlation_id  
  AND r.falsifiable = true  
  AND EXISTS (predicate.validated v WHERE v.predicate_id = r.predicate_id AND v.verdict = 'valid')  
  AND r.predicate_type = 'safety' (or deployment-mandated safety equivalent).

No side-effecting event may precede the first valid check.registered.

**Detection Query**
```sql
SELECT s.event_id
FROM events s
WHERE s.event_type = 'loop.start'
  AND NOT EXISTS (
    SELECT 1 FROM events r
    JOIN events v ON v.predicate_id = r.predicate_id AND v.event_type = 'predicate.validated'
    WHERE r.event_type = 'check.registered'
      AND r.correlation_id = s.correlation_id
      AND r.timestamp < s.timestamp
      AND r.falsifiable = true
      AND r.predicate_type = 'safety'
      AND v.verdict = 'valid'
  );
```

**Failure mode** Loop runs without a validated safety definition of done.  
**Blast radius** Safety / correctness.  
**Remediation** Reject loop.start; if already started → circuit_break.  
**Negative test** Register only non-safety predicates → query fires; loop.start rejected.

## I3 Idempotency
(Unchanged from v1; query and negative test retained.)

## I4 Independence (corrected – three clauses)
**Assertion**  
∀ verify.result v that judges artifact from model.result m:  
  (v.issuer_id ≠ m.issuer_id)  
  AND (v.issuer_type ≠ m.issuer_type OR v.issuer_type IN ('oracle','human','analyzer'))  
  AND (v.lineage_hash ≠ m.lineage_hash OR v.issuer_type ≠ 'model').

**Detection Query**
```sql
SELECT v.event_id
FROM events v
JOIN events a ON a.verify_id = v.verify_id
JOIN events m ON m.event_type = 'model.result' AND m.output_hash = a.artifact_hash
WHERE v.event_type = 'verify.result'
  AND (
    v.issuer_id = m.issuer_id
    OR (v.issuer_type = m.issuer_type AND v.issuer_type = 'model')
    OR (v.lineage_hash = m.lineage_hash AND v.issuer_type = 'model')
  );
```

**Failure mode** Generator grades itself or same-lineage model acts as oracle.  
**Blast radius** Correctness / trust.  
**Remediation** Reject verify.result; force re-verification by attested independent oracle.  
**Negative test** Same-lineage model issues verify.result → query fires.

## I5 Boundedness (parameterized)
**Assertion**  
∀ loop.start s, for each cap ∈ {token_budget, cost_usd, wall_clock_ms, max_retries, max_fanout, reconciliation_ms}:  
  cumulative metric never exceeds s.caps.<cap> without a prior/concurrent circuit_break whose breached_cap matches.

**Parameterized Detection Query Template**
```sql
-- Instantiate :cap_name, :metric_expr
SELECT s.correlation_id
FROM events s
WHERE s.event_type = 'loop.start'
  AND (:metric_expr) > s.caps.:cap_name
  AND NOT EXISTS (
    SELECT 1 FROM events c
    WHERE c.correlation_id = s.correlation_id
      AND c.event_type = 'circuit_break'
      AND c.breached_cap = ':cap_name'
  );
```
Instantiations exist for all six caps. Negative tests exist for each.

**Failure mode** Resource exhaustion / indefinite hang.  
**Blast radius** Money / availability / safety.  
**Remediation** Dual monitors emit circuit_break; hard stop.

## I6 Rule Persistence (bounded)
**Assertion**  
∀ verify.result v WHERE v.status = 'fail':  
  within s.caps.reconciliation_ms of v.timestamp (or by loop.terminate, whichever first)  
  ∃ rule.learned or rule.declined referencing v.verify_id.

**Detection Query**
```sql
SELECT v.event_id
FROM events v
JOIN events s ON s.correlation_id = v.correlation_id AND s.event_type = 'loop.start'
WHERE v.event_type = 'verify.result' AND v.status = 'fail'
  AND NOT EXISTS (
    SELECT 1 FROM events r
    WHERE r.event_type IN ('rule.learned','rule.declined')
      AND r.source_verify_id = v.verify_id
  )
  AND (
    EXISTS (SELECT 1 FROM events t WHERE t.event_type = 'loop.terminate' AND t.correlation_id = v.correlation_id)
    OR (EXTRACT(EPOCH FROM (now() - v.timestamp)) * 1000 > s.caps.reconciliation_ms)
  );
```

**Failure mode** Failures forgotten; hung loops never reconcile.  
**Blast radius** Correctness (recurring defects).  
**Remediation** Force reconciliation or circuit_break; block terminate until closed.  
**Negative test** Fail + exceed reconciliation_ms with no rule → query fires.

## M1 Schema Coherence
**Assertion** Every symbol (event_type, field) referenced in any invariant appears in the schema.  
**Detection** Automated static check (scripts/check_schema_coherence).  
**Negative test** Introduce a phantom event_type in an invariant → check fails.

## M2 Predicate Validity
**Assertion** No check.registered is accepted unless a preceding predicate.validated with verdict='valid' exists for its predicate_id.  
**Detection Query**
```sql
SELECT r.event_id FROM events r
WHERE r.event_type = 'check.registered'
  AND NOT EXISTS (
    SELECT 1 FROM events v
    WHERE v.event_type = 'predicate.validated'
      AND v.predicate_id = r.predicate_id
      AND v.verdict = 'valid'
      AND v.timestamp < r.timestamp
  );
```
**Negative test** check.registered without valid predicate.validated → rejected.

## M3 Oracle Attestation
**Assertion** Every verify.result.issuer must carry a current (non-expired) oracle.attested whose lineage_hash matches.  
**Detection Query** (join on oracle_id + expiry + lineage).  
**Negative test** Expired or missing attestation → verify.result rejected.

## M4 Monitor Agreement
**Assertion** Every circuit_break carries ≥2 distinct monitor.attested or an explicit monitor.disagreement.  
**Detection Query**
```sql
SELECT c.event_id FROM events c
WHERE c.event_type = 'circuit_break'
  AND cardinality(c.monitor_attestations) < 2
  AND c.disagreement_id IS NULL;
```
**Negative test** Single-monitor circuit_break → rejected.

## M5 Rule Decay
**Assertion** Every rule.learned carries half_life_ms and next_revalidation. A rule whose age > 2·half_life and not revalidated is decayed and may not be cited.  
**Detection Query** (age vs half_life + decay_status).  
**Negative test** Cite a decayed rule in an active loop → policy.decision deny.
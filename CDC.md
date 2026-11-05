# Carbon-Dating Changelog (CDC) Protocol

## Stratigraphy (Relative Dating)
- Each release is a numbered stratum L0, L1, … Ln.
- Every changelog entry and every log.notarized carries parent_hash of the preceding stratum.
- Ordering is derivable purely from the hash chain even if every clock is lying.

## Isotope Concordance (Absolute Dating)
Each change must carry ≥3 independent time sources from:
(a) monotonic host clock  
(b) signed external RFC 3161 timestamp  
(c) transparency-log inclusion proof  
(d) signed VCS commit timestamp  

**Concordance rule**: all present sources must lie within tolerance Δ (default 5 minutes).  
**Discordance action**: the change is quarantined into an undateable stratum; it is non-citable and must not be merged into a dated lineage. Never silently back-filled.

## Contamination Ratios
Record and threshold:
- human-authored vs agent-authored change ratio
- test-first vs test-after ratio (doctrine requires test-first; violation flags the stratum)
- reverted-change ratio

## Half-life & Decay
Every rule.learned and every mitigation carries half_life_ms.  
Re-validation due at T½; mandatory by 2·T½.  
Beyond 2·T½ → decay_status=decayed; rule may not be cited; must be rule.revalidated or rule.retired.

Calibration table (example):

| Rule Age | Required Evidence for Revalidation |
|----------|------------------------------------|
| < T½ | None (active) |
| T½ … 2·T½ | Fresh canary pass + secondary oracle sample |
| > 2·T½ | Full re-proof or retirement |

## Exclusions
Changes that cannot obtain ≥3 concordant sources are undateable: quarantined, non-citable, reported as explicit gaps.

## Changelog Entry Schema
```
change_id: UUID
stratum: string
parent_hash: string
timestamp_sources: array[≥3]
concordance_verdict: enum(concordant, discordant, undateable)
author_class: enum(human, agent, mixed)
test_first_evidence: object
invariants_touched: array
defects_closed: array
half_life_ms: integer
next_revalidation: RFC3339
decay_status: enum(active, pending, decayed)
anchor_proof: object
signature: string
```

## Detection Queries
- Undateable changes: concordance_verdict = 'undateable'
- Discordant timestamps: concordance_verdict = 'discordant'
- Decayed rules cited: join active loops against rules with decay_status='decayed'
- Test-after violations: test_first_evidence missing or false

## Worked Sample: v1.0 → v2.0 Transition

**Stratum L0** (v1.0 baseline)  
parent_hash: genesis  
timestamp_sources: [host, RFC3161, VCS]  
concordance: concordant  
defects_closed: []  
half_life: n/a  

**Stratum L1** (schema completion – closes D1/D2)  
parent_hash: L0  
timestamp_sources: [host, RFC3161, transparency-log, VCS]  
concordance: concordant  
defects_closed: [D1, D2, R1]  
invariants_touched: [M1]  
test_first_evidence: {tests: [AT-V2-001], committed_before: true}  
half_life_ms: 7776000000 (90 days)  

**Stratum L2** (invariant query fixes – closes D6–D9)  
parent_hash: L1  
… (concordant)  
defects_closed: [D6, D7, D8, D9, R2]  

**Stratum L3** (Falsifiability Engine + Canary + Dual Monitor – closes D3–D5)  
parent_hash: L2  
defects_closed: [D3, D4, D5, R4, R5, R6]  

**Stratum L4** (Trust anchor + CDC itself – closes D11, R8, R11)  
parent_hash: L3  
defects_closed: [D11, R8, R11]  

**Stratum U1** (deliberately undateable example)  
parent_hash: L3  
timestamp_sources: [host only]  
concordance_verdict: undateable  
action: quarantined; not merged; reported as gap in the public changelog  

This demonstrates the quarantine path.
# Defect Closure Table (D1–D14 + R1–R11)

Every item is closed. Closure evidence is an artifact in this repository. Verification query is executable against the v2.0 schema.

| ID | Defect | Closure Mechanism | Evidence Artifact | Verification Query / Check |
|----|--------|-------------------|-------------------|----------------------------|
| D1 | Schema–Invariant Drift | Complete event schema including all previously missing types; automated cross-reference | schemas/audit_event.v2.json + M1 invariant | Parse all invariants; assert every referenced event_type and field exists in schema enum |
| D2 | Incomplete event coverage | Added predicate.registered, predicate.validated, oracle.attested, monitor.attested, monitor.disagreement, policy.decision, canary.injected, canary.result, rule.revalidated, rule.retired, log.notarized | schemas/audit_event.v2.json | Schema enum contains every listed type |
| D3 | Self-declared falsifiability | Falsifiability Engine (Deliverable 4) required before predicate.validated | FALSIFIABILITY_ENGINE.md | No check.registered accepted without preceding predicate.validated |
| D4 | Oracle blind spot | Hidden rotating canary suite + oracle.attested with lineage hash | CANARY_SUITE.md + M3 | Canary injection produces canary.result; oracle.attested must be current |
| D5 | Monitor compromise | Dual-monitor architecture with agreement protocol | DUAL_MONITOR.md + M4 | circuit_break requires ≥2 monitor.attested or explicit monitor.disagreement |
| D6 | I2 query bug | Corrected detection query includes predicate_type='safety' | INVARIANTS.md I2 | Negative test: safety-less registration fires the query |
| D7 | I4 query bug | Full three-clause independence query (issuer_id, issuer_type, training lineage) | INVARIANTS.md I4 | Negative test: same-lineage oracle fails independence |
| D8 | I5 query incompleteness | Parameterized query template covering all six caps | INVARIANTS.md I5 | Template instantiated for each cap; negative tests exist |
| D9 | I6 unbounded "eventually" | Wall-clock-bounded reconciliation window independent of loop.terminate | INVARIANTS.md I6 | Hung loop still forces rule reconciliation or circuit_break |
| D10 | Human-in-the-loop contradiction | Goal sign-off is mandatory pre-flight gate with signed attestation; automated Intent Verification Oracle handles no-human path | AUDIT_PROCEDURE.md + INTENT_ORACLE.md | Ambiguity eliminated; both paths defined and tested |
| D11 | No external trust anchor | Merkle-root publication + RFC 3161 at stratum boundaries | TRUST_ANCHOR.md + log.notarized event | Auditor can verify external inclusion proof; unavailable anchor → fail closed |
| D12 | Procedure not executable | Corrected procedure written strictly against v2.0 schema | AUDIT_PROCEDURE.md | Every step references only defined events |
| D13 | Missing adversarial tests | Expanded matrix includes context-pollution, monitor split-brain, tautology, canary poisoning, clock-skew forgery | ACCEPTANCE_TESTS_v2.md | All D13 cases present with oracles |
| D14 | Self-audit gap | Meta-audit layer FLW-META-001…010 + recursion termination argument | META_AUDIT.md | Meta-rows exist and have falsifiable checks |
| R1 | Complete schema | Deliverable 1 | schemas/audit_event.v2.json | Zero orphan events/fields |
| R2 | Fix I2/I4/I5/I6 | Deliverable 2 | INVARIANTS.md | All queries match assertions + negative tests |
| R3 | Meta-audit flaw rows | ≥10 meta rows | META_AUDIT.md | FLW-META-001 to FLW-META-010 |
| R4 | Falsifiability Engine | Deliverable 4 | FALSIFIABILITY_ENGINE.md | Analyzer rejects tautologies with witness |
| R5 | Canary suite | Deliverable 5 | CANARY_SUITE.md | Rotation + poison-resistance defined |
| R6 | Dual monitors | Deliverable 6 | DUAL_MONITOR.md | Single compromised monitor cannot emit accepted circuit_break |
| R7 | Resolve D10 | Single adjudicated decision | AUDIT_PROCEDURE.md | No remaining ambiguity |
| R8 | Trust anchor | Deliverable 7 | TRUST_ANCHOR.md | External publication + fail-closed on unavailability |
| R9 | Rule half-life/decay | M5 + CDC | INVARIANTS.md M5 + CDC.md | Expired rules cannot be cited |
| R10 | Acceptance matrix v2 | Deliverable 9 | ACCEPTANCE_TESTS_v2.md | Every D-item and D13 case covered |
| R11 | CDC protocol | Deliverable 10 | CDC.md + sample changelog | ≥3 time sources, discordance policy, undateable quarantine |
# Meta-Audit Layer (FLW-META-001 … FLW-META-010)

These flaws apply to the audit system itself. Each has an executable falsifiable check.

| flaw_id | name | description | observable_signature | root_cause | blast_radius | severity | mitigation | falsifiable_check | residual_risk |
|---------|------|-------------|----------------------|------------|--------------|----------|------------|-------------------|---------------|
| FLW-META-001 | Schema–Invariant Drift | Invariants reference events/fields absent from schema | Cross-reference check fails | Incomplete schema evolution | Trust (audit system untrustworthy) | S1 | Automated M1 coherence check required before stratum accept | Introduce phantom event_type in invariant; assert M1 fails | Check itself has a bug |
| FLW-META-002 | Self-Declared Falsifiability | falsifiable=true is set by the party being audited | predicate.validated missing or verdict≠valid | No independent analyzer | Correctness | S1 | Falsifiability Engine mandatory | Inject tautology (x=x); assert rejection with witness | Analyzer incomplete for novel logics |
| FLW-META-003 | Oracle Blind Spot | Oracle never tested on unseen failures | canary.result absent or always pass | No hidden canary suite | Correctness / trust | S1 | Rotating hidden canary suite + attestation | Inject unseen canary; assert detection rate ≥ threshold | Canary suite itself poisoned |
| FLW-META-004 | Monitor Compromise | Single monitor can emit accepted circuit_break | circuit_break with <2 attestations | No dual-monitor requirement | Availability / safety | S0 | Dual-monitor + M4 | Single-monitor circuit_break; assert rejection | Both monitors collude |
| FLW-META-005 | Human-in-the-Loop Contradiction | Spec simultaneously requires and forbids human judgment | Ambiguous pre-flight path | Unresolved design tension | Correctness | S2 | Single adjudicated decision (mandatory signed attestation + Intent Oracle fallback) | Attempt loop.start with neither attestation nor Intent Oracle; assert rejection | Intent Oracle itself biased |
| FLW-META-006 | Trust-Anchor Absence | Hash chain only; no external publication | log.notarized missing at stratum boundary | Missing external anchor | Trust (attacker with write can rewrite history) | S1 | Mandatory Merkle + RFC 3161 at boundaries | Stratum without notarization; assert fail-closed | External TSA compromised |
| FLW-META-007 | Rule Immortality | Rules never decay or re-validated | rule.learned with age > 2·half_life still cited | No half-life mechanism | Correctness (stale rules) | S2 | M5 + CDC decay | Cite decayed rule; assert policy deny | Half-life set too long |
| FLW-META-008 | Context-Pollution in Diff | Failing diff itself contains injection payload | retry.scheduled.minimal_diff fails injection scan | No sanitization of feedback | Security | S1 | Injection scan + size cap on minimal_diff | Inject payload in diff; assert scan reject | Novel injection form |
| FLW-META-009 | Schema Evolution Without Migration | New required field added; old events become invalid | Old events fail new schema validation | No versioned migration | Observability | S2 | Explicit schema_version + migration events | Validate old event against new schema; assert controlled handling | Migration loses data |
| FLW-META-010 | Recursion Without Termination | "Who audits the auditor" has no base case | Infinite meta-audit regress | Missing termination argument | Availability (process never ends) | S3 | Explicit base case: external transparency log + human oversight committee with published charter is the terminal auditor; further recursion is out of scope and logged as accepted residual risk | Attempt to require meta-meta-audit; assert termination clause fires | Terminal auditor is itself captured |

## Recursion Termination Argument
The audit system is not required to be self-auditing to infinite regress. The terminal trust anchor is:
1. External transparency log (publicly verifiable inclusion proofs), and
2. A named human oversight committee whose charter, membership, and decision log are themselves published to the same transparency log.

Any further "who audits the committee" is declared residual risk and accepted under the Fail-Closed doctrine: if the terminal anchor is unavailable or demonstrably compromised, the system refuses to start new loops (fail closed). This is the explicit base case.
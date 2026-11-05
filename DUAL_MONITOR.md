# Dual-Monitor Protocol (closes D5)

## Independence Requirements
- Two monitors must have distinct issuer_id, distinct deployment (process/host), and distinct code lineage (or one is a formally verified reference monitor).
- Monitors may not share mutable state except the append-only log.

## Agreement Rule
A circuit_break is accepted only if:
- ≥2 distinct monitor.attested events cite the same breached_cap and values within tolerance, or
- an explicit monitor.disagreement is recorded and escalated according to policy (default: fail closed / human escalation).

## Split-Brain Handling
If monitors disagree beyond tolerance:
1. Emit monitor.disagreement.
2. Suspend further side-effecting acts for the correlation_id.
3. Escalate to the Intent / Safety Oracle or human committee.
4. Do not accept a unilateral circuit_break.

## Proof Obligation
A single compromised monitor cannot cause an accepted circuit_break. This is enforced by M4 and tested by ADV-MONITOR-SPLIT.
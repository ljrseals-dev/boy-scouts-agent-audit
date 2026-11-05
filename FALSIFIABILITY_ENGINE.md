# Falsifiability Engine Specification (closes D3)

## Purpose
Independent analyzer that validates a predicate before it may be used in check.registered. Self-declaration of falsifiable=true is forbidden.

## Rejection Classes
1. **Tautology** — predicate is true in all models (e.g., x = x, true ∨ P).
2. **Vacuous** — predicate is true only because its antecedent is unsatisfiable.
3. **Unsatisfiable** — predicate is false in all models (no artifact can ever pass).
4. **No reachable counterexample** — analyzer cannot produce a concrete witness that would make the predicate false, and the predicate is not proven valid by a complete decision procedure.

## Required Outputs
- verdict ∈ {valid, tautology, vacuous, unsatisfiable, no_counterexample}
- counterexample_witness (required when verdict ≠ valid) — a concrete input that falsifies the predicate
- analysis_hash

## Analyzer's Own Oracle
The Falsifiability Engine is itself subject to the canary suite (see CANARY_SUITE.md). Its lineage_hash must be attested. It may not validate its own predicates.

## Canaries Specific to the Engine
- Known tautologies
- Known unsatisfiable predicates
- Borderline predicates that require a non-trivial counterexample search

Pass criterion: 100% rejection of planted tautologies/unsatisfiables; ≥95% production of usable counterexample witnesses on a held-out set.

## Integration
predicate.registered → Falsifiability Engine → predicate.validated (only verdict=valid is accepted by check.registered).
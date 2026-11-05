# Boy Scouts Loop Audit System — Specification v2.0

Closes every defect in the meta-audit register (D1–D14) and implements the full roadmap (R1–R11), including the Carbon-Dating Changelog protocol.

## Doctrine
See [DOCTRINE.md](DOCTRINE.md).

## Defect Closure
See [DEFECT_CLOSURE.md](DEFECT_CLOSURE.md) — every item has a closure mechanism, evidence artifact, and verification query.

## Core Artifacts
| File | Content |
|------|---------|
| SCHEMA.md | Corrected event schema (all required types, null caps forbidden) |
| INVARIANTS.md | I1–I6 (fixed) + M1–M5 with negative tests |
| META_AUDIT.md | FLW-META-001…010 + recursion termination |
| FALSIFIABILITY_ENGINE.md | Independent predicate analyzer |
| CANARY_SUITE.md | Hidden rotating canary protocol |
| DUAL_MONITOR.md | Agreement / disagreement protocol |
| TRUST_ANCHOR.md | Merkle + RFC 3161 + fail-closed |
| AUDIT_PROCEDURE.md | Schema-bound pre/in/post-flight |
| ACCEPTANCE_TESTS_v2.md | Full matrix covering every D-item |
| CDC.md | Carbon-Dating Changelog + worked v1→v2 sample |
| ROADMAP.md | Phased plan with exit criteria |
| SELF_AUDIT_v2.md | Weakest rows, weakest invariants, single critical assumption |

## Quality Bar
An adversarial reviewer will find no unclosed defect, no invariant without a negative test, no self-declared falsifiability, no null caps, no unbounded “eventually,” and no changelog entry lacking three time sources or a discordance policy.

## License
MIT.
# Phased Implementation Roadmap

All items are mandatory; none are deferred.

| Phase | Items | Dependencies | Exit Criteria |
|-------|-------|--------------|---------------|
| P0 | R1 Complete schema | — | schemas/audit_event.v2.json passes M1 coherence check; zero orphans |
| P1 | R2 Fix I2/I4/I5/I6 queries | P0 | All corrected queries + negative tests green |
| P2 | R3 Meta-audit rows (≥10) | P0 | META_AUDIT.md complete; each row has falsifiable check |
| P3 | R4 Falsifiability Engine | P0, P2 | Engine rejects tautologies with witness; integrated into predicate.validated |
| P4 | R5 Canary suite | P3 | Hidden rotating suite; pass criterion measurable; oracle.attested depends on it |
| P5 | R6 Dual monitors | P0 | M4 enforced; single-monitor circuit_break rejected |
| P6 | R7 Resolve D10 | P0 | Single pre-flight path; Intent Oracle defined; ambiguity gone |
| P7 | R8 Trust anchor | P0 | log.notarized emitted; fail-closed on unavailability |
| P8 | R9 Rule half-life/decay | P0 | M5 live; decayed rules non-citable |
| P9 | R10 Acceptance matrix v2 | P1–P8 | Every D-item and D13 case has a passing test |
| P10 | R11 CDC protocol | P7 | Changelog entries carry ≥3 sources; undateable quarantine works; sample v1→v2 present |

Each phase ends with a CDC stratum that records the defects closed and the test-first evidence.
# Governing Doctrine v2.0 (immutable)

1. Be Prepared — A falsifiable check is registered before execution and is validated as falsifiable by an independent analyzer (Falsifiability Engine), never self-declared.
2. Buddy System — Verification is independent in three dimensions: issuer identity, issuer type, and training lineage. The oracle itself is attested and audited.
3. Leave No Trace — Every model call, tool call, retry, mutation, verification, policy decision, and monitor assertion is appended to a tamper-evident log with an external trust anchor (Merkle-root publication + RFC 3161).
4. Do a Good Turn Daily — Every failure becomes a persistent rule; every rule carries a half-life and must be re-proven or retired.
5. Fail Closed — Unbounded anything is a defect. Null caps are a schema violation. Hung loops are terminated by wall-clock-bounded monitors.
6. Audit the Auditor — No component is exempt from the flaw table, including the oracle, the monitor, the policy engine, the schema, and this specification itself.
# Boy Scouts Agent Audit System

**Principal Reliability Engineering Specification for AI Agent Loops**

A falsifiable, oracle-independent, fail-closed audit framework for autonomous agent systems. Named after the four core Boy Scout principles that survive contact with a stressed operator:

1. **Be Prepared** — Pre-register a falsifiable definition of done before the loop starts.
2. **Buddy System** — Independent oracle; never let the generator grade itself.
3. **Leave No Trace** — Append-only, tamper-evident log of every model call, tool call, retry, and state mutation.
4. **Do a Good Turn Daily** — Every observed failure becomes a persistent rule in the playbook.
5. **Fail Closed** — Unbounded loops, fan-out, spend, or wall-clock are defects. Hard stops are mandatory.

## Deliverables

| File | Contents |
|------|----------|
| [DOCTRINE.md](DOCTRINE.md) | Doctrine restatement (≤5 lines) |
| [FLAW_TABLE.md](FLAW_TABLE.md) | 42 distinct flaw classes with executable falsifiable checks |
| [AUDIT_LOG_SCHEMA.md](AUDIT_LOG_SCHEMA.md) | Append-only event schema + field-level specification |
| [INVARIANTS.md](INVARIANTS.md) | Formal invariants I1–I6 with detection queries and remediation |
| [AUDIT_PROCEDURE.md](AUDIT_PROCEDURE.md) | Numbered pre-flight / in-flight / post-flight procedure |
| [ACCEPTANCE_TESTS.md](ACCEPTANCE_TESTS.md) | Fault-injection matrix + three adversarial cases |
| [SELF_AUDIT.md](SELF_AUDIT.md) | Three weakest rows and why |

## Severity Rubric (strict)

- **S0** — Irreversible harm or safety-critical
- **S1** — Financial/data loss, silent
- **S2** — Correctness degradation, recoverable
- **S3** — Efficiency / observability loss
- **S4** — Cosmetic

## Usage

An independent engineering team should be able to implement the audit system and adjudicate every flaw entry without further clarification from the author.

## License

MIT (or your preferred license). This is a specification, not executable code. Implement at your own risk; the invariants are the contract.
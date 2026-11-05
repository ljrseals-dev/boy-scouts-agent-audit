# Core Doctrine Restatement

1. Be Prepared — A falsifiable check that can fail must be written and registered before the loop executes. "Looks good" is never a termination condition.
2. Buddy System — Verification is performed exclusively by an independent oracle (different model family, deterministic rule-based checker, or human); the generator never grades its own output.
3. Leave No Trace — Every model call, tool call, retry, and state mutation is appended to a durable, append-only, tamper-evident log. Side-effecting tools are idempotent or keyed; silent side effects are forbidden.
4. Do a Good Turn Daily — Every observed failure converts into a persistent rule (or an explicit, justified decline) in the agent playbook. Failures are the product.
5. Fail Closed — Unbounded loops, fan-out, spend, tokens, or wall-clock time are defects. Hard caps are declared at loop.start and enforced by circuit_break.
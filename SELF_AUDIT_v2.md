# Self-Audit v2

## Three Weakest Rows in the v2.0 Meta-Audit Table
1. **FLW-META-010 (Recursion Without Termination)**  
   The termination argument relies on an external transparency log and a human oversight committee. If both are captured, the base case fails. This is acknowledged residual risk, but it is the softest underbelly of the whole system.

2. **FLW-META-003 (Oracle Blind Spot)**  
   Canary effectiveness depends on the canary generator remaining uncompromised and on the detection threshold θ being set appropriately. A sophisticated adaptive oracle could still drift between canary rotations.

3. **FLW-META-007 (Rule Immortality)**  
   Half-life assignment is still a human/policy choice. Setting all half-lives to “very long” re-introduces the original immortality problem under a different name.

## Three Weakest Invariants
1. **M5 (Rule Decay)** — Depends on correct half-life calibration and on the policy engine actually consulting decay_status. Enforcement is only as strong as the policy decision point.
2. **I4 (Independence)** — Lineage_hash quality is only as good as the model-provider’s honesty about training lineage. Providers can lie.
3. **M4 (Monitor Agreement)** — Dual monitors can still collude if they share a common dependency or operator.

## Single Assumption That, If False, Invalidates the Whole System
**The external trust anchor (transparency log + RFC 3161 TSA) is not under the control of the same adversary that can write to the local log.**  

If that assumption is false, an attacker with write access can rewrite history and also control the “external” notarization, rendering Leave No Trace and the entire CDC chronometry theater. All other mechanisms (dual monitors, canaries, falsifiability engine) become local claims without an independent referee. This is the single point on which the whole edifice rests; it is therefore called out explicitly and the fail-closed policy on anchor unavailability is non-negotiable.
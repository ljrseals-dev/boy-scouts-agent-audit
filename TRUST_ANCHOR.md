# Trust-Anchoring Specification (closes D11)

## Mechanism
At every CDC stratum boundary (and at configurable intervals inside long-running loops):
1. Compute Merkle root over the ordered event hashes of the stratum.
2. Obtain an RFC 3161 timestamp token over the Merkle root from an external Time-Stamp Authority.
3. Submit the Merkle root + timestamp to a public transparency log (or equivalent append-only public log) and obtain an inclusion proof.
4. Emit log.notarized containing merkle_root, external_timestamp, transparency_log_proof, stratum_id.

## Verification Procedure
An auditor:
1. Recomputes the Merkle root from the local event stream.
2. Verifies the RFC 3161 token.
3. Verifies the transparency-log inclusion proof.
4. Checks that the stratum parent_hash chain is consistent.

## Unavailability Policy (Fail Closed)
If the external timestamp authority or transparency log is unavailable at a required notarization point:
- New loop.start is rejected.
- In-flight loops are allowed only a bounded grace period (declared in caps) then forced to circuit_break.
- No silent continuation.

This closes the "hash chain alone is recomputable by a write-capable attacker" defect.
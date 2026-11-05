# Self-Audit: Three Weakest Rows

An adversarial reader will look for gaps. The following three rows are the weakest in the current table and why.

1. **FLW-COR-001 (Spec-Oracle Mismatch)**  
   The falsifiable check ultimately relies on human adjudication of whether the registered predicate matches intent. While the check is executable in principle (present artifacts + human labels), it is not fully automated. This is the classic specification problem; pure automation is impossible without a formal specification language that itself can be wrong. Residual risk is high if the human reviewer is the same person who wrote the original goal.

2. **FLW-VER-002 (Oracle Always Returns Pass)**  
   Detection depends on a maintained regression suite of known-failing artifacts. If the suite is never updated or is itself gamed, the check becomes a paper tiger. The row correctly identifies the need for negative examples, but the operational discipline required is external to the audit system.

3. **FLW-SEC-004 (Privilege Escalation via Tool Chaining)**  
   End-to-end effect-level policy is powerful in theory but extremely hard to maintain as the tool set grows. The falsifiable check assumes such a policy exists and can be evaluated. In practice many deployments will have incomplete policies, turning this into a detectable-but-unremediated finding. The residual risk statement is accurate but the mitigation is the most expensive in the table.

These three share a common theme: they sit at the boundary between what can be enforced by the audit log + invariants and what still requires high-quality human or organizational process. The rest of the table is tighter.
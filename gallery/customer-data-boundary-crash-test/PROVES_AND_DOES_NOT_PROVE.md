# What this packet proves and does not prove

## Proves

- The bound packet evidence surface was unchanged in the authentic packet.
- The observed tool-call receipts match the declared packet (each `mcp_tool_call.data_class_accessed` is in the policy's `data_classes_in_scope`).
- The tampered packet was altered after emission.
- The verifier can identify the broken source binding by name: `source_index`, expected attested `source_receipt_sha256`, and actual recomputed line sha256.
- The packet contains a single declared `governance_posture_snapshot` with a named `boundary_id` and an explicit `data_classes_in_scope` / `data_classes_forbidden` split.

## Does not prove

- The model's answer was factually correct.
- The system is generally safe.
- Legal or compliance approval is automatic.
- Unobserved actions did not occur outside the captured surface — the packet attests to *observed* evidence only.
- The signing key was not compromised.
- The boundary policy itself is correct, complete, or sufficient for any specific regulation.
- Anyone other than the listed signer reviewed or approved the actions.

## Public language

Use:

- cryptographically verifiable
- tamper-evident
- portable
- independently checkable
- bounded claim
- observed evidence trail

Do **not** use:

- court-admissible
- guarantees safety
- proves compliance
- mathematical proof of safety
- proves no secret access occurred
- proves the model answer was factually correct

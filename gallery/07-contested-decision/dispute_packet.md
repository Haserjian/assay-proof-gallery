# Dispute Packet: Contested Vendor Decision

**Scenario:** A vendor disputes an AI-assisted procurement recommendation
one week after the evaluation. They claim their proposal was strongest and
the selection of Vendor B was incorrect. The ops team must reconstruct what
happened and respond with defensible evidence.

---

## Path A: Reconstruction from operational systems

**Available sources:** Slack, email, procurement dashboard, staff memory
**Time:** ~3 hours

The ops team tries to answer basic questions:
- When did the evaluation run?
- Who triggered it?
- Which policy or scoring rubric was active?
- Which proposal files were actually evaluated?
- Why was Vendor B selected?

They find partial clues, but no sealed record.

### Step 1: Find the decision (30 min)

"When did we run this evaluation?" No decision log. Search Slack for
"vendor evaluation" — three threads, none with a final decision record.
Search email — one thread mentions a recommendation but no policy details.
Check the procurement dashboard — it shows current-state data, not the
view at evaluation time.

**Gap:** No record of when the evaluation ran or who triggered it.

### Step 2: Identify what policy was active (25 min)

"Was the standard scoring rubric active, or the updated one?" Check the
policy folder — two versions, neither dated. Ask the procurement lead
via Slack. Response: "I think we switched to v2 that week, but v1 might
have still been active for some evaluations." Ambiguous.

**Gap:** Cannot confirm which policy version governed this evaluation.

### Step 3: Reconstruct the inputs (40 min)

"What proposals were submitted, and what scores did the model assign?"
Re-pull the proposal files from the shared drive. Two of three are still
there. The third was updated by the vendor after the evaluation. No proof
the current version matches what the model saw.

**Gap:** Input authenticity is unverifiable. The vendor's updated proposal
may differ from what was evaluated.

### Step 4: Reconstruct the reasoning (35 min)

"Why was Vendor B selected?" No decision log. Interview the analyst — they
remember "something about cost-efficiency scoring" but not the specific
policy check. Email the procurement director — out of office.

Write a best-effort explanation: "We believe the decision was based on
the standard scoring rubric favoring cost-efficiency. Possibly also
compliance factors."

**Gap:** Reasoning reconstructed from memory, not the evaluation record.

### Step 5: Respond to the vendor (30 min)

Draft response: "Our evaluation indicated Vendor B scored highest on our
procurement criteria during the evaluation window."

Caveat added: "We are working from reconstructed data. We cannot guarantee
this matches the original evaluation exactly. We recommend re-evaluating
under current conditions if you wish to contest further."

### Result

~3 hours. 4 people involved. 2 unresolvable gaps. 1 caveat.

**What is missing:**
- Exact execution timestamp
- Actor or trigger identity
- Governing policy version at runtime
- Proof that evaluated inputs match the original inputs
- Signed rationale tied to the actual run
- Any artifact the vendor can verify independently

---

## Path B: Signed decision packet

**Available sources:** `assay verify-pack`, the signed proof pack
**Time:** ~2 minutes

### Step 1: Verify the packet (15 sec)

```
$ assay verify-pack ./proof_pack

PASS
Pack ID:     pack_20260330T210728_9710cb47
Integrity:   PASS (Ed25519 signature valid, all hashes match)
Claims:      PASS (3 receipts >= 2 required)
Receipts:    3
```

The packet is intact. Nothing was altered after signing.

### Step 2: Read the evidence (1 min)

The receipts answer every question the vendor raised:

| Question | Answer in the packet |
|----------|---------------------|
| When did the evaluation run? | Timestamp sealed at execution time |
| What execution environment was used? | Model: `claude-sonnet-4-20250514`, provider: Anthropic, 3102 tokens |
| What task was performed? | `vendor_proposal_evaluation` |
| Which policy gate ran? | `procurement_policy_gate` |
| What policy version governed the run? | `vendor_scoring_rubric` v2.1, digest: `sha256:a4f1c9e2...` |
| Was the evaluation in scope? | Yes: "within declared procurement scope, no PII in proposals" |
| What was the output? | File write to `/output/vendor_decision.json`, authorized |
| How do we know this wasn't assembled later? | Manifest hash closure + Ed25519 signature. Any byte change fails verification. |

### Step 3: Respond to the vendor (30 sec)

Forward the proof pack and verification transcript.

> "Attached is the signed decision packet and verification transcript for
> the evaluation. The packet can be verified offline with our public key.
> It records the execution facts, policy gate result, and authorized output
> for this run."

No reconstruction caveat needed. The remaining caveats are explicit, bounded,
and cryptographically testable (see "What the packet does NOT prove" below).

### Result

~2 minutes. 1 person. Verifiable chain for the recorded decision path. Signed.

---

## What the packet proves — three layers

### Integrity proof
The packet has not been altered since signing.
- Manifest hashes match
- Signature verifies
- Changing any byte causes verification failure

### Execution proof
This evaluation run occurred as recorded.
- Timestamp, task, model, provider, token counts, output artifact

### Governance proof
The recorded policy gate allowed the action under declared scope at runtime.
- Policy: `vendor_scoring_rubric` v2.1
- Policy digest: `sha256:a4f1c9e2d7b83056f1e9ca234d6781ab09ef3c7d`
- Verdict: allow
- Risk score: 0.12

---

## What the packet does NOT prove

- That every action in the system was recorded
- That the vendor proposals were authentic or unmodified in the real world
- That the model's recommendation was correct, fair, or unbiased
- That this was the only evaluation ever run
- That the signer key was never compromised
- That timestamps were externally anchored (local clock was used)

It proves what was recorded and signed at execution time, not the
real-world truth of upstream inputs — unless those inputs were themselves
authenticated.

---

## Trust boundary

| | |
|---|---|
| **Signed by** | `assay-local` (operator-held key) |
| **Trust assumption** | Signer faithfully recorded the episode at execution time |
| **Not covered unless separately authenticated** | Upstream documents, real-world facts, input authenticity |

---

## One-line summary

Without a signed decision packet:
"We reconstructed the decision as best we could."

With a signed decision packet:
"Here is the original execution record. You can verify it yourself."

That is the product.

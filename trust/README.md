# Trust Policy

This directory contains the signer registry and acceptance rules
for Assay proof pack verification in CI.

## Quick start

1. Find your signer fingerprint:
   ```
   assay key list
   ```

2. Add the fingerprint to `signers.yaml` under `signers:`
   (replace the commented placeholder)

3. Generate a proof pack: `assay run -- <your command>`

4. Commit `trust/`, the proof pack, and push.
   Trust evaluation appears in the next PR comment.

**Note:** The generated workflow sets `require-pack: true`.
If your repo does not produce proof packs on every PR,
set `require-pack: false` in `.github/workflows/assay-verify.yml`.

## Files

| File | Purpose |
|------|---------|
| `signers.yaml` | Who is allowed to sign proof packs |
| `acceptance.yaml` | What decisions apply per signer status and target |

## Verification levels

| Level | Meaning |
|-------|---------|
| `signature_verified` | Ed25519 signature valid, signer fingerprint extracted |
| `hash_verified` | File hashes match manifest, no signature check |
| `unverified` | No verification performed |

## Reviewer packet examples

- [Scenario 05: reviewer-packet-gaps](https://github.com/Haserjian/assay-proof-gallery/tree/main/gallery/05-reviewer-packet-gaps) — buyer-facing
- [Scenario 06: naic-aiset-mapping](https://github.com/Haserjian/assay-proof-gallery/tree/main/gallery/06-naic-aiset-mapping) — compliance/regulatory

## Upgrading trust posture

| From | To | Change |
|------|----|--------|
| minimal | reviewer | Edit `acceptance.yaml`: change `unrecognized` decision from `accept` to `warn` |
| reviewer | strict | Edit workflow: add `enforce-trust: true`. Edit `acceptance.yaml`: change `unrecognized` from `warn` to `reject` |

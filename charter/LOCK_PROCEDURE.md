# LOCK PROCEDURE — retraction-retrodiction Design-A charter

**Status: `DRAFT`. This is a staged checklist. Nothing here runs until the operator says
"lock"** — expected on the August clock, not before. The charter
(`design_A_charter_DRAFT.md`) is folded to binding in structure; the steps below are the
mechanical acts that convert it from `DRAFT` to `LOCKED`.

Run the steps **in order**. Each is either `[OPERATOR]` (needs your credentials/identity or
your explicit word) or `[AGENT]` (mechanical, already built and rehearsed). The full,
top-to-bottom operator path — including the two credentialed steps in detail — is in
[`../WALKTHROUGH.md`](../WALKTHROUGH.md).

---

## Preconditions (the four lock gates — all must be green)

- **Gate 1 — contact identity.** `config/contact.yaml` exists with a real, email-shaped
  `contact_email` (not the placeholder). The network guard in `recon/probe.py` passes.
  NCBI API key optional but recommended (WALKTHROUGH Gate 1b).
- **Gate 2 — program home.** `papanokechi/retraction-retrodiction` exists on GitHub, the
  founding commit is pushed, and the file inventory matches the local tree (WALKTHROUGH Gate 2b/2c).
- **Gate 3 — pin machinery.** `scripts/pin_snapshots.py --dry-run` resolves all five sources
  live (rehearsed 2026-07-14: OpenAlex `2026-06-25`, RW, Crossref `2026`, PMC, OpenCitations `January 2026`).
- **Gate 4 — ledger witnessed.** Every gate-passing commit is pushed to `origin` before the next
  phase starts (**R-PUSH**), and the proposal ledger is externally deposited, so the pre-threshold
  ordering claim rests on an archived timestamp rather than a local commit date. See
  *Standing rules* in `charter/PROPOSAL_LEDGER.md` (**R-COW**, **R-PUSH**) and entry JC9-003.
  **Pins must not be taken while the ledger commit is unpushed or undeposited.**

---

## Lock sequence (ordered — do not reorder)

1. **`[OPERATOR]` Confirm Gate 1.** Verify `config/contact.yaml` holds your real email (and,
   ideally, your NCBI API key). Sanity-check the guard:
   ```bash
   python -m pytest tests/ -q            # -> 8 passed
   python scripts/pin_snapshots.py --dry-run   # network calls succeed => guard is satisfied
   ```

2. **`[OPERATOR]` Confirm Gate 2.** Confirm the repo is live and the push landed
   (WALKTHROUGH Gate 2b). The agent verifies remote reachability + founding-commit
   file inventory (WALKTHROUGH Gate 2c).

3. **`[AGENT, on your word]` Pin the snapshots for real.**
   ```bash
   python scripts/pin_snapshots.py --pin
   ```
   This downloads a **fresh** Retraction Watch CSV (records date, row count, SHA-256), reads
   the current OpenAlex release ID, Crossref annual-file year + torrent DOI, PMC
   `PMC-ids.csv.gz` date, and OpenCitations dump, and writes `charter/snapshot_pins.yaml`
   (each entry: value, retrieval timestamp, source URL, hash where applicable). Commit it:
   ```bash
   git add charter/snapshot_pins.yaml
   git commit -m "chore(lock): pin lock-day snapshots (Gate 3)"
   ```

4. **`[AGENT, on your word]` Flip the charter status `DRAFT` -> `LOCKED`.** In the
   `design_A_charter_DRAFT.md` header, set the status to `LOCKED` and record the **lock
   timestamp** and the **git SHA** of the pinning commit from step 3. Commit:
   ```bash
   git commit -am "chore(lock): charter DRAFT -> LOCKED (<timestamp>, pins @ <sha>)"
   ```

5. **`[AGENT, on your word]` Tag the founding state.**
   ```bash
   git tag charter-lock-v1
   git push origin main --tags
   ```

6. **`[BINDING, from this commit forward]` Amendments only.** After `charter-lock-v1`, the
   charter changes only by **amendment with an audit trail**, per the §8 invariants
   (locked-YAML-before-data, verbatim-cell, matched-random-null + placebo-relative floor,
   never silently edit a locked field). Any revision is a new lock, never an in-place edit.

---

## What lock does **not** authorize

Locking the charter starts the **week-one build** (harvest module + tests + manifests
*before any question is asked of the data*). It does **not** authorize skipping the
guard cascade, writing per-observable preregistration YAMLs ahead of their data, or
computing any verdict-bearing quantity before its observable's locked prereg exists.
Those remain gated exactly as in Program 1.

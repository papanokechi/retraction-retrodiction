# Proposal ledger — pre-threshold integrity record

Purpose: make *"the thresholds were chosen before any outcome data was touched"* **checkable**
rather than asserted. Each entry records a document in its **blank-threshold** state, so any later
version can be diffed against a digest that provably predates the numbers.

This file is append-only. Entries are never edited or removed; a superseded entry gets a successor
row, not a correction.

## Standing rules

**R-COW — copy-on-write for ledgered artifacts.** Any file that has a ledger entry is **never
overwritten in place**. A new revision is a **new file** (`…_rev4.md`, not a rewrite of `…_rev3.md`)
**plus** a new entry. The digest of every entry must remain **reproducible from a held artifact**;
an entry whose subject no longer exists is an attestation to a blob nobody has. Adopted after
JC9-001 was rendered unreproducible by hash-then-overwrite (see JC9-003).

**R-PUSH — push per gate.** Every gate-passing commit is pushed to `origin` **before the next phase
starts**. A commit that exists only in a working copy is a mutable local fact, not an attestation:
the working tree lives in a session directory that is subject to garbage collection, and committer
dates are author-settable. R-COW closes this failure at the file layer; R-PUSH closes the same
failure at the commit layer.

*Scope note: pushing buys **immutability under third-party custody** — content cannot be silently
altered afterwards. It does **not** buy a trustworthy clock. For ordering claims that must survive a
hostile referee rather than a curious one, the durable instrument is an external archival deposit
with an independent timestamp (Zenodo DOI), not the git history alone.*

---

## JC9-001 — `charter/PROPOSED_JC9_target_definition.md`, blank-threshold state

| field | value |
|---|---|
| **SHA-256** | `eacfa854f2fcd9a00a1e97b2eb012aa812bc1fbbe43972f910b0b18d062bc861` |
| **Size** | 27,218 bytes |
| **Recorded (UTC)** | 2026-07-27T00:07:43Z |
| **Repo state at recording** | `440e63f` · no tags · `charter/snapshot_pins.yaml` absent |
| **Charter state** | `design_A_charter_DRAFT.md` **DRAFT, untouched** (0 diff lines) |
| **Proposal state** | **untracked** — not committed, so a rejectable proposal never enters public history |
| **Outcome data touched** | **none** — no pins taken, no harvest run, no score computed |

### What is provably blank at this digest

| unset quantity | where |
|---|---|
| `Δ₁` — F1 equivalence margin | §0.3 F1 |
| `Δ₂` — F2 equivalence margin | §0.3 F2 |
| F3 per-stratum margins | §0.3 F3 |
| The **quantile** selections for all frozen-null thresholds | §0.3 construction rule |
| F0 cluster-adjusted event floor | §0.3 F0 |
| **JC9-OP** — max falsely-flagged papers per correctly-flagged paper | §0.3 JC9-OP |

Every one of these is either (a) **derived** from a frozen null distribution once the operator
selects a *quantile*, or (b) in the single case of **JC9-OP**, an explicit operator value judgment
recorded as prose. **None is an absolute number chosen by the agent.**

### How to check this later

```powershell
# 1. Confirm the blank version still hashes to the recorded digest
Get-FileHash charter\PROPOSED_JC9_target_definition.md -Algorithm SHA256

# 2. Diff any threshold-filled version against the blank one to see exactly
#    which values were added, and confirm nothing else moved
git diff <blank-blob> <filled-blob> -- charter/PROPOSED_JC9_target_definition.md
```

A filled version whose non-threshold text differs from the blank version is **an amendment**, not a
threshold entry, and is governed by the §8 audit-trail invariants.

### Ordering claim this entry supports

> The falsification thresholds of JC9 were fixed **after** this digest and **before** any outcome
> data existed — because at this digest no snapshot was pinned, no corpus was harvested, and no
> score had been computed.

That claim is checkable against three independent facts recorded above: the absent
`snapshot_pins.yaml`, the tagless repo at `440e63f`, and this digest.

---

## JC9-002 — same document, rev 3, blank-threshold state — **CURRENT**

Supersedes JC9-001 for ordering purposes. **JC9-001 is not removed and remains a valid record of
the rev-2 state** (this ledger is append-only: a superseded entry gets a successor row, never a
correction).

| field | value |
|---|---|
| **SHA-256** | `d50fa1bb334cc88c1e042c6f0e339f3dd1ddad58efacf7efb2cf75f748e19843` |
| **Size** | 34,496 bytes |
| **Recorded (UTC)** | 2026-07-27T00:12:33Z |
| **Supersedes** | JC9-001 (`eacfa854…bc861`, 27,218 bytes) |
| **Repo state at recording** | `440e63f` · no tags · `charter/snapshot_pins.yaml` absent |
| **Charter state** | `design_A_charter_DRAFT.md` **DRAFT, untouched** (0 diff lines) |
| **Proposal state** | **untracked** — deliberately uncommitted |
| **Outcome data touched** | **none** |

### What changed between JC9-001 and JC9-002 (all structural, none numeric)

| # | change |
|---|---|
| 1 | **Claim licensing is affirmative-only (default-deny)** — `INDETERMINATE` and `INFEASIBLE` now leave a claim `UNLICENSED`. Rev 2 assigned consequences to two of three states and let the third revert to the pre-F1 default, re-opening the two-branch defect through a different door. |
| 2 | **`INDETERMINATE` pre-declared as the modal outcome** at 0.036% with cluster-adjusted counts, so the expected branch is not read as failure when it arrives. |
| 3 | **JC9-OP becomes a pair `(k, c)`** — a coverage floor `c` closes the free parameter by which precision could be bought by shrinking the flag set; the operating point is now *derived* (threshold at recall `c`), not chosen. |
| 4 | **`Reason` mapping gains paper-level resolution rules** — flaw-implicating dominance for multi-code records (with the mixed share reported), unmapped-codes-default-to-`ambiguous` so post-pin vocabulary drift is visible rather than silent, and `non-flaw` pre-declared expected-`INFEASIBLE`. |
| 5 | **Artifact discipline downgraded from a protection claim to a publication decision** — aggregate-only release does **not** prevent reconstruction and no longer says it does. |

**Verification of the blank state at this digest:** no numeric value is assigned to `k`, `c`, `Δ₁`,
`Δ₂`, the F3 per-stratum margins, the F0 cluster-adjusted floor, or any threshold quantile. Audited
by pattern scan at recording time; the only numerals in the document are the base rate (0.036%),
the §1 background ratio (2,766×), and cross-references to charter sections and predecessor findings.

### Why this entry is committed and the proposal is not

The ledger entry contains **a digest and a byte count** — it is not the rejectable artifact; the
proposal is. Committing the ledger **alone** converts the ordering claim from three local, mutable
facts into a **git-timestamped attestation**, at the cost of one commit, without putting a proposal
that may be rejected into public history.

---

## JC9-003 — integrity repair: JC9-001 unreproducible; JC9-002 recorded pre-push

This entry records **two defects in the ledger's own integrity**, and the standing rules adopted in
response. It creates no new digest of the proposal and changes no threshold state.

| field | value |
|---|---|
| **Recorded (UTC)** | 2026-08-01T05:08:32Z |
| **Subject** | this ledger's JC9-001 and JC9-002 entries |
| **Repo state at recording** | local `3eef116` · `origin/main` `440e63f` (**local ahead 1, unpushed**) · no tags · `charter/snapshot_pins.yaml` absent |
| **Charter state** | `design_A_charter_DRAFT.md` **DRAFT, untouched** (0 diff lines) |
| **Proposal state** | rev 3, **untracked**, `d50fa1bb…19843`, 34,496 bytes — unchanged, still blank-threshold |
| **Outcome data touched** | **none** — no pins, no harvest, no score |

### Defect 1 — JC9-001's digest is unreproducible

`eacfa854f2fcd9a00a1e97b2eb012aa812bc1fbbe43972f910b0b18d062bc861` (27,218 bytes) cannot be
reproduced from any held artifact.

**Cause: hash-then-overwrite of an untracked file.** Rev 2 was digested into JC9-001, then edited
**in place** to produce rev 3. Because the proposal is deliberately uncommitted, git held no copy,
so the rev-2 bytes were destroyed by the edit. The deliberate-non-commit decision was sound; what
was missing was the rule that a ledgered file is revised by **addition**, not by overwrite.

**Disposition.** JC9-001 is **not removed** — this ledger is append-only and the entry remains a
valid record of *what was attested at that time*. It is marked here as **unreproducible**: it can no
longer be verified by re-hashing, only relied upon as a prior statement. It is superseded for all
ordering purposes by **JC9-002**, whose subject **is** held and **does** re-hash correctly.

**Load-bearing status: none lost.** The ordering claim never rested on JC9-001's digest alone. It
rests on the independent facts recorded at entry time — **no snapshot pinned, no corpus harvested,
no score computed, charter DRAFT and untouched, repo tagless** — all four of which remain true as of
this entry, and all four of which are independently checkable today.

**Rule adopted:** **R-COW** (see *Standing rules*, above).

### Defect 2 — JC9-002 was committed but not pushed

JC9-002 states that committing the ledger *"converts the ordering claim from three local, mutable
facts into a git-timestamped attestation."* At time of this entry **that conversion had not
occurred**: commit `3eef116` existed only in a working copy under a chat-session directory
(`.copilot/chats/…`), which is subject to garbage collection, and `origin/main` was still at
`440e63f`. An unpushed commit is a **fourth mutable local fact**, not an attestation.

**Also recorded: JC9-002's commit preceded Phases 0–2 of the activation runbook.** The ledger was
committed out of the runbook's order. This does not damage the ordering claim it attests — the four
independent facts above were all true at commit time — but the phase is spent and cannot be re-run.

**Rule adopted:** **R-PUSH** (see *Standing rules*, above).

### Why both defects are the same defect

Lost rev 2 and the unwitnessed attestation are one failure at two layers: **work that exists only in
a session directory.** R-COW closes the file layer; R-PUSH closes the commit layer. Neither is a
statement about thresholds, and neither changes the blank-threshold state recorded by JC9-002.

### Nothing is reserved

Ledger IDs are assigned as `max + 1` at time of writing. **No ID is reserved for any future entry.**
The threshold-derivation entry contemplated by the activation runbook will take whatever ID is next
when it is actually written.

### Blank-threshold state is unchanged

No value is assigned to `k`, `c`, `Δ₁`, `Δ₂`, the F3 per-stratum margins, the F0 cluster-adjusted
floor, or any threshold quantile. **Six quantities unset; JC9-OP unruled.** This entry is an
integrity repair, not a threshold entry.

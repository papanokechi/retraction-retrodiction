# WALKTHROUGH — path to lock for the retraction-retrodiction charter

This is the **single top-to-bottom path** from "charter drafted" to "ready to lock." Read it
in order. Every step is marked:

- **`[DONE-AGENT]`** — mechanical work, already built, tested, and rehearsed. Nothing for you to do.
- **`[OPERATOR]`** — needs your credentials or identity (the two credentialed steps: **Gate 1b**
  NCBI API key, **Gate 2b** GitHub push).

> **Discipline: nothing is locked.** This document *stages* the path. The charter stays
> `DRAFT`, no snapshot is pinned, and no build starts until you say **"lock"** — expected on
> the August clock. (**Gate 2 is now complete** — the repo is public and pushed, 2026-07-14;
> that is *publication of the founding state*, **not** a lock.) The ordered lock-day sequence
> itself lives in [`charter/LOCK_PROCEDURE.md`](charter/LOCK_PROCEDURE.md); this walkthrough
> gets you to its door.

Gate status: **Gate 1** (contact email + NCBI) — *operator paste pending*; **Gate 2** (repo
creation) — **✅ complete 2026-07-14**; **Gate 3** (snapshot pins) — *staged for lock day*.
Each has its agent-automated parts and, where needed, your numbered steps.

---

## Gate 1 — contact email + NCBI registration

### 1a `[DONE-AGENT]` — placeholder swept, contact identity is now config-sourced

Every hardcoded `recon@example.org` in **code** was found and removed. The sweep hits and their fixes:

| File:line (before) | Was | Now |
|---|---|---|
| `recon/probe.py` (`MAILTO=`) | module constant `recon@example.org` | derived from `config/contact.yaml` via `contact_email()` |
| `recon/p02b_rw_size.py` (~:26) | hardcoded `mailto` | imports `MAILTO` from `probe` |
| `recon/p04_pubmed.py` (:8, :50) | hardcoded `tool`/`email` | imports `NCBI_TOOL`, `CONTACT_EMAIL` from `probe` |
| `recon/p01_openalex.py`, `recon/p02_crossref.py` | already derived `MAILTO` from `probe` | unchanged (no hit) |

The value now comes from one place — **`config/contact.yaml`** (gitignored) — with a committed
template at **`config/contact.example.yaml`**. The only surviving `recon@example.org` strings are
intentional and non-functional: the guard's rejected-placeholder set (`recon/probe.py`), the test
constant (`tests/test_contact_guard.py`), the template's doc comment, and the recon report's flags.

**You do this once (also step 1 of the quickstart):**

```bash
cp config/contact.example.yaml config/contact.yaml
# edit config/contact.yaml -> contact_email: "you@your-institution.example"
```

### 1b `[OPERATOR]` — NCBI E-utilities: what to register, and where the values land

The recon report's R1 flag says the NCBI `tool`/`email` must be *registered, not merely supplied*.
Verified live against the E-utilities docs (`ncbi.nlm.nih.gov/books/NBK25497/`, 2026-07-14), the
current mechanism is:

- **`tool` and `email` are self-declared parameters — there is no separate registration to file.**
  You simply send them on every request; NCBI uses them to contact you before throttling. They are
  already staged in `config/contact.yaml` (`ncbi_tool: retraction-retrodiction`, and `email` inherits
  `contact_email`).
- **An API key is optional and recommended** — it lifts the E-utilities rate limit from **3 → 10
  requests/second**. This is the "registration" worth doing.

**Numbered steps to create the API key:**

1. Sign in (or create a free account) at **`https://www.ncbi.nlm.nih.gov/account/`**. If you use
   institutional or ORCID sign-in, that is fine.
2. Click your username (top-right) → **Account settings**.
3. Scroll to the **API Key Management** panel.
4. Click **Create an API Key**. A long hex string appears immediately.
5. Copy it.

**Where each value lands in `config/contact.yaml`:**

```yaml
contact_email: "you@your-institution.example"   # your real address (Crossref + OpenAlex + NCBI email)
ncbi_tool:     "retraction-retrodiction"        # already set; self-declared, no registration
ncbi_api_key:  "PASTE_THE_HEX_KEY_HERE"         # from step 4-5 above; leave "" to run keyless at 3 req/s
```

**Polite-pool notes for the same file (no registration, just identity):**

- **Crossref** — sending a `mailto` puts you in Crossref's *polite pool* (faster, more reliable).
  `crossref_mailto` is blank by default and **inherits `contact_email`**; set it only to override.
- **OpenAlex** — OpenAlex's 2026 freemium model replaced the old `mailto` polite pool with an API
  key (free $0.10/day keyless, $1/day with a free key). Because **every verdict-bearing quantity
  uses the CC0 snapshot, not the live API** (charter §9), a key is dev convenience only. Fill
  `openalex_api_key` / `openalex_mailto` if you want the faster dev loop; otherwise leave them `""`.

> When done, tell the agent — this is JC7, and its flag stays open in the charter (§13.1) until
> you confirm `config/contact.yaml` is filled.

### 1c `[DONE-AGENT]` — startup network guard + tests

`recon/probe.py`'s `get()` and `head()` now call `require_contact()` **before any network call**.
If `contact_email` is missing, still the placeholder, not email-shaped, or a reserved-example
domain, the harness raises `RuntimeError` and **no request goes out**. Verified:

- `tests/test_contact_guard.py` — **5/5 pass** (guard fires on the placeholder; passes on a real-shaped
  value; `RRP_CONTACT_EMAIL` override honored).
- End-to-end: with the placeholder config in place, `python recon/p01_openalex.py` **refuses** with a
  `RuntimeError` instead of probing OpenAlex.
- Full hermetic suite (`python -m pytest tests/ -q`): **8 passed**.

---

## Gate 2 — repo creation: `papanokechi/retraction-retrodiction`

### 2a `[DONE-AGENT]` — local repo assembled + founding commit

This repository is the founding-state assembly. Structure:

```
retraction-retrodiction/
├── README.md                 program blurb + charter pointer + predecessor DOI + license note
├── LICENSE                   CC BY 4.0 (docs / charter / recon prose)
├── LICENSE-CODE              MIT (recon/*.py, scripts/*.py, tests/*.py — SPDX-headed)
├── WALKTHROUGH.md            this file
├── .gitignore                config/contact.yaml, data/, the 65 MB RW CSV, __pycache__, ...
├── charter/
│   ├── design_A_charter_DRAFT.md   THE charter (staged for lock; §2 references snapshot_pins.yaml)
│   └── LOCK_PROCEDURE.md            the ordered lock-day checklist
├── recon/
│   ├── README.md             probe inventory + RW CSV re-fetch route
│   ├── datasets_scouting_report.md, probe_log.jsonl, sample_records.json
│   └── probe.py + p0*.py     the read-only probe harness
├── config/
│   ├── contact.example.yaml  committed template
│   └── contact.yaml          GITIGNORED (present locally, never committed)
├── scripts/pin_snapshots.py  Gate 3 automation
└── tests/                    test_contact_guard.py, test_pin_yaml.py  (8 tests, hermetic)
```

- The **65 MB Retraction Watch CSV is not committed** (gitignored); its re-fetch route is in
  `recon/README.md`.
- Suite re-verified green **from this repo layout** (`probe.py`'s config search walks upward, so it
  still finds `config/contact.yaml` after the move into `recon/`): **8 passed**, and
  `pin_snapshots.py --dry-run` resolves all 5 sources live.
- Founding commit created locally as a single clean root commit: `chore: found
  retraction-retrodiction program (charter + recon evidence + lock-gate automation)` at
  **`976bb41`**, carrying the standard `Co-authored-by` + `Copilot-Session` trailers.
  **28 tracked files** (`config/contact.yaml` and the 65 MB RW CSV correctly excluded;
  `LICENSE` + `LICENSE-CODE` both present). Pushed in Gate 2b (below).

### 2b `[DONE — agent-executed under operator approval]` — create the GitHub repo and push

> **✅ Executed 2026-07-14 15:14, agent-side, under explicit operator approval in-dialog.**
> This step was originally designated `[OPERATOR]` because it creates a **public** repo under
> your identity. The operator approved the agent running it live in the session, so the record
> and the actual git history reconcile *here, on the record*, rather than in memory. The repo
> is live and public: **https://github.com/papanokechi/retraction-retrodiction**
>
> Command used (the fast path, option below): `gh repo create papanokechi/retraction-retrodiction --public --source=. --remote=origin --push`. The manual instructions that follow are retained for reproducibility and for anyone re-running this from scratch.

**Step 1 — create the empty repo on GitHub.** Go to **`https://github.com/new`** and set:
- **Owner:** `papanokechi`  ·  **Repository name:** `retraction-retrodiction`
- **Public**
- **Do NOT** add a README, `.gitignore`, or license (the founding commit already has them; an
  auto-init would create a conflicting root commit).
- Click **Create repository**. Leave the "…or push an existing repository" page open.

**Step 2 — add the remote and push.** From the repo directory
(`retraction-retrodiction/`), assuming your existing auth from the `siarc-relay-bridge`
setup works:

```bash
git remote add origin https://github.com/papanokechi/retraction-retrodiction.git
git branch -M main
git push -u origin main
```

**Fastest path (if you have the GitHub CLI):** it creates the repo *and* pushes in one line — skip
Step 1:

```bash
gh repo create papanokechi/retraction-retrodiction --public --source=. --remote=origin --push
```

**Fallback if auth fails** (the `siarc-relay-bridge` credential didn't carry over):
- **HTTPS + token:** create a fine-grained PAT (`https://github.com/settings/tokens`) with
  *Contents: read/write* on this repo, then `git push` and paste the token as the password; or
- **GitHub CLI:** `gh auth login` (choose GitHub.com → HTTPS → browser), then retry the push; or
- **SSH:** ensure your key is in `https://github.com/settings/keys`, then use the SSH remote
  `git remote set-url origin git@github.com:papanokechi/retraction-retrodiction.git` and push.

> Do **not** push tags yet — `charter-lock-v1` is created on lock day (LOCK_PROCEDURE step 5), not now.

### 2c `[DONE-AGENT]` — verified ✅

Verified 2026-07-14 against the live remote: reachable and **public**, default branch `main`;
remote HEAD `976bb41` **== local HEAD**; **file inventory exact 28 == 28** (remote tree == local
tree); `config/contact.yaml` **absent** and the 65 MB RW CSV **absent** (both correctly
gitignored); `LICENSE` + `LICENSE-CODE` both present; **no tags** (`charter-lock-v1` correctly
reserved for lock day, per LOCK_PROCEDURE step 5). **Gate 2 complete.**

---

## Gate 3 — snapshot pins

### 3a `[DONE-AGENT]` — `scripts/pin_snapshots.py` written and rehearsed

One command records lock-day state into `charter/snapshot_pins.yaml`. It is **`--dry-run` by
default** (proves the lookups resolve, pins nothing); `--pin` does the real thing on lock day.
Dry-run **2026-07-14, all five sources live**:

| Source | Dry-run value | Route |
|---|---|---|
| OpenAlex | release `2026-06-25` | `openalex.s3.amazonaws.com/RELEASE_NOTES.txt` (CC0; `s3://openalex/data`) |
| Retraction Watch | `65,073,315` bytes (fresh CSV date/rows/SHA-256 recorded at `--pin`) | GitLab raw CSV (CC0) |
| Crossref | `2026` public data file (+ torrent DOI) | `crossref.org/.../public-data-file/` |
| PMC OA | `PMC-ids.csv.gz` Last-Modified `2026-07-13` | `ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz` |
| OpenCitations | `January 2026` index dump | `download.opencitations.net` (CC0) |

It bypasses the Gate-1 harvest guard on purpose (it reads only public CC0 artifacts, so the
dry-run runs today under placeholder config), and the YAML writer is unit-tested
(`tests/test_pin_yaml.py`, 3/3) so a pinned `2026-06-25` round-trips as a string, not a date.

### 3b `[DONE-AGENT]` — charter §2 rewired to the pin keys

The five `☐ TO BE PINNED AT LOCK` checkboxes in the charter's §2 source table now reference
`snapshot_pins.yaml` keys (`sources.openalex`, `sources.retraction_watch`, …) plus the dry-run
values, with a note that pinning is mechanical. **Lock day is now just running the script.**

### 3c `[OPERATOR, on lock day only]` — pin for real

Not now. On lock day, per `charter/LOCK_PROCEDURE.md` step 3:

```bash
python scripts/pin_snapshots.py --pin        # writes charter/snapshot_pins.yaml
git add charter/snapshot_pins.yaml && git commit -m "chore(lock): pin lock-day snapshots (Gate 3)"
```

---

## After the three gates: lock day

When Gate 1 is filled, Gate 2 is pushed and verified, and you give the word, follow
**[`charter/LOCK_PROCEDURE.md`](charter/LOCK_PROCEDURE.md)** in order: pin (3) → flip charter
`DRAFT`→`LOCKED` with timestamp + SHA (4) → tag `charter-lock-v1` (5) → amendments-only from
there (6). Locking starts the week-one build (harvest module + tests + manifests *before any
question is asked of the data*) — and nothing before then.

**Nothing in this walkthrough is locked, pushed, pinned, or built. That all waits for your word.**

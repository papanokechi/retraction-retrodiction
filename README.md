# retraction-retrodiction

**A pre-registered retrodiction study of retraction precursors** — do papers that are
*later* retracted carry detectable anomalies (in reference structure, citation dynamics,
self-citation, and — secondarily — abstract semantics) *before* the retraction notice,
relative to matched controls drawn from a strictly broader background corpus? The design
is **retrodiction-calibrated**: success criteria are frozen in a locked charter *before*
any verdict-bearing quantity is computed, and the guard cascade that governed the
predecessor program is re-instantiated here at conception.

This is **Program 2** in a portfolio. It inherits its method discipline — and its
guard cascade (Table 1 of the charter) — from **Program 1** (arXiv fusion retrodiction),
published to Zenodo:

> Papanokechi (2026). *Retrodiction-calibrated science mapping: a pre-registered null
> and an artifact taxonomy for embedding-based field-fusion detection.*
> Zenodo. **DOI [10.5281/zenodo.21334050](https://doi.org/10.5281/zenodo.21334050)**
> (concept DOI `10.5281/zenodo.21334049`, always-latest).

## Charter (start here)

The design is governed by a single charter, staged for final lock:

- **[`charter/design_A_charter_DRAFT.md`](charter/design_A_charter_DRAFT.md)** — pinned
  snapshot sources (§2), event rule (§3, Retraction Watch `RetractionNature == "Retraction"`),
  date semantics (§4), strata (§5), observables hierarchy (§6, metadata/citation-structure
  **primary**, full-text **secondary/coverage-gated**), the three-arm control-matching
  design (§7, **C primary / D co-primary sensitivity / A third arm; B rejected**), the
  guard-cascade inheritance block (§8 + the §8.1 sign-by-stratum hypothesis table), and
  the sequence to lock (§13–§14).
- **[`charter/LOCK_PROCEDURE.md`](charter/LOCK_PROCEDURE.md)** — the ordered lock-day
  checklist. **Status: `DRAFT` — nothing in this repo is locked.**

## Recon evidence

The charter's dataset choices trace to a read-only reconnaissance phase (94 timestamped
probes, verify-don't-recall):

- **[`recon/datasets_scouting_report.md`](recon/datasets_scouting_report.md)** — per-dataset
  factsheets (OpenAlex, Crossref, Retraction Watch, Semantic Scholar / S2ORC, PubMed / PMC,
  OpenCitations, replication sets, arXiv-linkage), the A/B/C × R1–R6 feasibility matrix,
  the risk register, and the recommendation.
- **[`recon/probe_log.jsonl`](recon/probe_log.jsonl)** — every probe, timestamped; each
  report number traces to a `probe_id` or a cited page.
- **[`recon/README.md`](recon/README.md)** — the probe-script inventory and the
  Retraction Watch CSV re-fetch route (the 65 MB CSV is **not** committed).

## Lock-gate automation (Gates 1 & 3)

Everything mechanical for lock day is built and tested:

| Gate | What | Where |
|------|------|-------|
| **1a/1c** | Config-sourced contact identity + a network guard that refuses every API call until a real email is set (placeholder-proof) | `recon/probe.py`, `config/contact.example.yaml`, `tests/test_contact_guard.py` |
| **3a** | One-command snapshot pinning (`--dry-run` default; `--pin` writes `charter/snapshot_pins.yaml` on lock day) | `scripts/pin_snapshots.py`, `tests/test_pin_yaml.py` |

The two steps that require operator credentials/identity — **NCBI API-key registration**
and **the GitHub push** — are written up as a numbered top-to-bottom path in
**[`WALKTHROUGH.md`](WALKTHROUGH.md)**.

## Quickstart

```bash
# 1. Set your real contact identity (Gate 1 — the harness refuses network calls until you do)
cp config/contact.example.yaml config/contact.yaml
#   then edit config/contact.yaml: contact_email: "you@your-institution.example"
#   (config/contact.yaml is gitignored and never committed)

# 2. Run the hermetic test suite (no network)
python -m pytest tests/ -q            # -> 8 passed

# 3. Prove the lock-day snapshot lookups resolve, live, without pinning anything
python scripts/pin_snapshots.py --dry-run
```

The contact guard is deliberately strict: it rejects empty values, non-email-shaped
strings, the historical `recon@example.org` placeholder, and RFC-2606 reserved domains
(`example.com/.org/.net`, `.test`, `.invalid`, `.localhost`). Set `RRP_CONTACT_EMAIL`
to override the config file (used by CI).

## Licensing

This repository is **dual-licensed by content type** (the split is machine-verifiable —
every `.py` file carries an `SPDX-License-Identifier` header):

- **Documentation, charter, and recon evidence** — all `.md` files (README, charter,
  scouting report), plus `recon/probe_log.jsonl` and `recon/sample_records.json`:
  **[CC BY 4.0](LICENSE)**.
- **Code** — `recon/*.py`, `scripts/*.py`, `tests/*.py`: **[MIT](LICENSE-CODE)** (each
  file headed `# SPDX-License-Identifier: MIT`).

Rationale: CC BY is a *content* license and creates attribution ambiguity when applied to
source, which MIT resolves cleanly — so the probe harness and pinning machinery stay
reusable downstream while the prose stays CC BY 4.0. This also matches how the predecessor
program's code (DOI 10.5281/zenodo.21334050) will likely be relicensed.

## Status

`DRAFT` — the charter is **staged for final lock**, not locked. No harvesting pipeline,
no preregistration YAMLs, and no build exist yet by design: week-one build starts on the
August clock, after lock (see `charter/LOCK_PROCEDURE.md`).

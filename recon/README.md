# recon/ — dataset reconnaissance evidence

Read-only scouting phase for the retraction-retrodiction program (all probes run
**2026-07-14**, verify-don't-recall). Nothing here harvests a corpus or computes a
similarity — it is API probes and documentation reads, every one logged.

## Deliverables

| File | What |
|------|------|
| `datasets_scouting_report.md` | Per-dataset factsheets, the A/B/C × R1–R6 feasibility matrix, the risk register, and the recommendation (reasoning separated from evidence). |
| `probe_log.jsonl` | Every probe, timestamped (`probe_id`, endpoint, response summary) + verbatim doc-reads. Each number in the report traces here. |
| `sample_records.json` | The 24-record cross-source join fixture (retracted + ordinary papers) used for the join-key and event-date spot checks. |

## Probe scripts (read-only harness)

All import the shared harness `probe.py`, which sources the contact email from
`../config/contact.yaml` (Gate 1) and refuses network calls until it is set.

| Script | Dataset / purpose |
|--------|-------------------|
| `probe.py` | Shared read-only harness: contact-config loader + network guard, `get`/`head`, `log_probe`. |
| `p01_openalex.py` | OpenAlex probe battery; generates the linked sample used across sources. |
| `p02_crossref.py` | Crossref + Retraction Watch (update-type:retraction) probes. |
| `p02b_rw_size.py` | RW bulk-file size (HTTP Range) + Labs API shape. |
| `p02c_rw_download.py` | One-time RW CSV bulk-route download + R2/R4/R6 analysis (see re-fetch route below). |
| `p02d_rw_peryear.py` | Per-year true-`Retraction` counts, re-derived from the **cached** CSV (no re-download). |
| `p02e_backfill_diag.py` | JC3 backfill diagnostic: is the 2010–11 `RetractionDate` spike genuine old-paper backfill, or imputed founding-era notice dates? (Ruling: keep membership, exclude pre-2012 notice dates from timing.) |
| `p03_s2.py` | Semantic Scholar Graph API + S2ORC datasets route. |
| `p03b_s2orc.py` | S2ORC datasets route + citation-context coverage. |
| `p04_pubmed.py` | PubMed E-utilities + PMC retraction counts, per-year, ID linkage (uses `ncbi_tool` + `contact_email`). |
| `p05_opencitations.py` | OpenCitations Index v2 citation counts + join fields. |
| `p05b_oc_fields.py` | OpenCitations field-level shape. |
| `log_doc_reads.py` | Appends license/rate-limit/attribution doc-read findings to `probe_log.jsonl`. |

## Retraction Watch CSV — re-fetch route (the 65 MB CSV is NOT committed)

The Retraction Watch database is distributed **via Crossref** as a single CSV, **CC0**.
It is ~65 MB and is deliberately excluded from git (see the repo `.gitignore`). It
re-downloads in seconds:

```bash
# canonical bulk route (public, CC0) — as used by p02c_rw_download.py
curl -L -o retraction_watch.csv \
  "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
```

or, staying inside the harness (which also logs the fetch to `probe_log.jsonl`):

```bash
cd recon
python p02c_rw_download.py
```

> **Reproducibility note.** The recon copy was fetched 2026-07-14. For the lock,
> `scripts/pin_snapshots.py --pin` downloads a **fresh** CSV and records its date,
> row count, and SHA-256 into `charter/snapshot_pins.yaml` — the recon copy is *not*
> reused, so the lock pins lock-day state (see `charter/LOCK_PROCEDURE.md`).

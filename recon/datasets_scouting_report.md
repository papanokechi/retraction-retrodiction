# Dataset Reconnaissance — Retrodiction-Calibrated Research-Integrity / Meta-Science Program

**Phase:** Read-only dataset scouting (no pipelines, no harvesting, no similarity computation)
**Reconnaissance date:** 2026-07-14 (Asia/Tokyo)
**Analyst artifacts:** `probe_log.jsonl` (93 timestamped entries — 71 live API/bulk probes + 22 verbatim documentation reads), `sample_records.json` (24-record cross-source join fixture), `retraction_watch.csv` (65 MB, one-time bulk-route confirmation).
**Predecessor program constraining this choice:** arXiv fusion retrodiction, DOI [10.5281/zenodo.21334050](https://doi.org/10.5281/zenodo.21334050).

> **Discipline note.** This report separates **evidence** (measured probes + verbatim documentation, each tagged with a `probe_id` traceable to `probe_log.jsonl`) from **reasoning** (the recommendation section). Every number traces to a probe or a cited page fetched live on 2026-07-14. Nothing is asserted from memory. Where a fact could not be confirmed by a live fetch it is marked **UNVERIFIED**.

> **⚠️ Placeholder flag (carry to any production harvest).** All probes used `mailto=recon@example.org` — a reserved-example placeholder in `probe.py`. Before any production run the operator **must** substitute a real contact email for the Crossref/OpenAlex polite pools and the NCBI `tool`/`email` registration (the latter must be *registered*, not merely supplied — see §5).

---

## 0. Headline findings (for the impatient)

1. **The retraction event layer is strong and over the power floor by orders of magnitude.** Three independent retraction counts — OpenAlex `is_retracted` **115,496**, Crossref `update-type:retraction` **73,501**, Retraction Watch true-`Retraction` **65,598** (biomedical-only PubMed adds **33,173**) — all far exceed R4's 50/stratum floor, with thousands per year. **Design A (retraction precursors) is the recommended primary.**
2. **The count divergence is itself a first-class R2 finding.** A ~1.75× spread across sources reflects *definition and curation differences* (all-fields vs Crossmark-deposited vs RW-curated vs MeSH-typed), not error. Any design must **pre-register one authoritative event source + inclusion rule**.
3. **Retraction Watch is the event backbone** — CC0, day-level `RetractionDate` **and** `OriginalPaperDate`, typed `RetractionNature`, controlled-vocabulary `Reason`, and **both DOIs + both PubMedIDs** as join keys (OriginalPaperDOI complete **96.2%**). Daily-updated, one 65 MB CSV.
4. **Full text is the binding constraint, not events.** Only **5/12** sample retracted papers resolved to a PMC full-text ID; OpenAlex abstracts present for only **14/30 (47%)** of retracted works; Semantic Scholar citation *contexts* are **sparse on the free API (0–5 / 50)**. Any semantic/context precursor signal is bounded by full-text coverage of the retracted set.
5. **Design B (replication calibration) is feasible only as a single pooled cross-section**, not as a temporal retrodiction: pooled clean **N ≈ 1,200–1,800** replication pairs (FReD-dominated), psychology-heavy, with per-year strata well below the R4 floor.
6. **Two access-model changes land inside the program window.** OpenAlex moved from the free `mailto` polite pool to an **API-key freemium** model (bulk snapshot stays free/CC0); PMC's **`oa.fcgi` web service is removed August 2026** (replaced by the `s3://pmc-oa-opendata` cloud service). Both must be designed around.

---

## 1. Per-dataset factsheets

### 1.1 OpenAlex — likely backbone (metadata + retraction flag + background)

| Property | Finding | Evidence |
|---|---|---|
| Total works | **319,512,759** | `OA-A` (live) |
| Retracted works (`is_retracted:true`) | **115,496** — filter confirmed to exist | `OA-B` (live) |
| Retractions / year | 2020 **8,348** · 2021 **13,034** · 2022 **16,898** · 2023 **18,434** · 2024 **12,623** · 2025 7,401 | `OA-C` (live) |
| Retracted-sample completeness (n=30) | DOI **30/30** · PMID/PMCID 25/30 · references **30/30** · **abstract 14/30 (47%)** · topic 30/30 · pubdate 30/30 | `OA-E` (live) |
| Ordinary-sample completeness (n=30) | DOI 28/30 · references 27/30 · abstract 24/30 (80%) · topic 30/30 | `OA-F` (live) |
| License | **CC0 1.0** ("complete dataset is free under the CC0 license"); non-binding citation request (Priem et al. 2022) | `OA-LIC` |
| Bulk route | `s3://openalex`, `aws s3 sync … --no-sign-request`, **free** (AWS Open Data); gz JSONL ~**330 GB** / ~1.6 TB decompressed; Parquet rolling out; **quarterly** (free) | `OA-BULK` |
| **Rate/access model change (2026)** | Polite-pool `mailto` **replaced** by freemium API key: **$0.10/day free (no key)**, $1/day (free key); List+Filter $0.10/1k calls, Search $1/1k, **singleton by ID/DOI free**; >100 req/s ⇒ 429. **Bulk snapshot remains free.** | `OA-RATE` |
| Join keys | DOI (near-complete), PMID/PMCID (partial), `referenced_works`, `topics`, `authorships` | `OA-E/F` |
| R5 redeposit | CC0 ⇒ derived embeddings/extracts freely redepositable to Zenodo under CC-BY | `OA-LIC` |

**Role:** the metadata + citation + background spine. `is_retracted` gives a ready target flag; the 319.5 M corpus gives an enormous background pool. **Caveat:** abstract coverage on the retracted set is weak (47%) — OpenAlex is a linkage/background layer, not a full-text source.

### 1.2 Crossref — metadata + typed update events

| Property | Finding | Evidence |
|---|---|---|
| Total works | **184,417,576** | `CR-A` (live) |
| `update-type:retraction` | **73,501** | `CR-B` (live) |
| Sample resolution | **12/12** retracted DOIs resolve | `CR-C`,`CR-D` (live) |
| Event representation | Inconsistent per record: some `relation.retraction`, most `updated-by` (n=1–5), some landmark cases empty `relation` but `updated-by:2`. `updated-by` carries **typed, day-level** events (`retraction`/`expression_of_concern`/`correction`) + notice DOI | `CR-C` (live) |
| `source` provenance | Updates flagged `publisher` vs `retraction-watch`; **12 update-types** incl. `retraction`,`partial_retraction`,`withdrawal`,`removal`,`expression_of_concern` | `CR-UPD` |
| License | Bibliographic metadata + references = **facts / not copyrightable**; Crossref-generated = **CC0**; **abstracts = publisher/author COPYRIGHT** | `CR-LIC` |
| Rate limits (eff. 2025-12-01) | Public 5/s single, 1/s list; **Polite (mailto) 10/s single, 3/s list**; Plus 150/s | `CR-RATE` |
| Bulk route | Annual public data file, JSONL tar, 2026 = **208 GB** / ~180 M records; Academic Torrents `doi.org/10.13003/nggf-vt1j` + AWS requester-pays (~$18) | `CR-BULK` |

**Role:** the typed-event and reference-metadata layer; the `source` field lets you separate publisher-asserted from RW-asserted events — useful for an R2 sensitivity analysis. **Caveat:** abstracts are copyright (not redepositable); linkage representation is non-uniform, so events are better taken from RW.

### 1.3 Retraction Watch (RWDB, via Crossref) — the R2 event backbone

| Property | Finding | Evidence |
|---|---|---|
| Access route | GitLab `crossref/retraction-watch-data` (CSV, **daily**) + Labs API `api.labs.crossref.org/data/retractionwatch` (CSV stream). Both live. | `RW-A`,`RW-ROUTE` |
| File | **65,073,315 bytes (~65 MB)**, 21 columns; README generated 2026-07-13 | `RW-SIZE`,`RW-FIELDS` |
| Rows | **71,027** total: **Retraction 65,598** · Expression of concern 3,580 · Correction 1,490 · Reinstatement 160 · blank 199 | `RW-ANALYZE` (live parse) |
| Join-key completeness | OriginalPaperDOI **96.2%** · OriginalPaperPubMedID 92.5% · RetractionDOI 99.0% · RetractionPubMedID 92.5% · RetractionDate/OriginalPaperDate/Reason/Subject **99.7%** | `RW-ANALYZE` |
| Dates | Day-level (`MM/DD/YYYY 0:00`); **both** retraction date and original-paper date | `RW-FIELDS` |
| True-`Retraction`/year (by `RetractionDate`) | 2010 **5,010** · 2011 4,935 · 2012 1,158 · … · 2022 5,564 · 2023 **13,204** · 2024 6,135 · 2025 5,523 | `RW-YEAR` |
| License | **CC0** (Crossref licensing table; no LICENSE file in repo, 404) | `RW-FIELDS`,`RW-ROUTE` |
| Documented biases | EoC/corrections "**not as comprehensive as retractions**"; `RetractionDate` = date of *published notice*, not misconduct/discovery; discovery via mixed methods | `RW-FIELDS` |

**Two visible temporal biases to pre-register around:** the **2010–2011 spike** (~5,000/yr — a curation backfill of older records) and the **2023 spike** (13,204 — the Hindawi/IEEE mass-retraction wave). Neither is a uniform "retraction rate."

### 1.4 Semantic Scholar / S2ORC — citation contexts + full text

| Property | Finding | Evidence |
|---|---|---|
| Sample resolution | **11/12** retracted resolve by DOI; 1 ordinary 404 | `S2-LOOKUP`,`S2-AGG` (live) |
| Fields on sample | OA-PDF **11/11** · abstract 6/11 · **arXiv 0/12** (biomedical) · reference/citation counts present | `S2-LOOKUP` |
| **Citation contexts (Design C core)** | **Sparse on free Graph API:** 0/50 on a landmark CS paper, **5/50** on a biomed paper (real snippets, uneven). `intents` rarer (1/50). | `S2-CONTEXTS2` (live) |
| Datasets (release 2026-07-07) | `abstracts,authors,citations,embeddings-specter_v1/v2,paper-ids,papers,publication-venues,s2orc,s2orc_v2,tldrs` | `S2ORC-LIST` (live) |
| S2ORC gating | Download endpoint returns **401 "A valid API key is required"** without a key | `S2ORC-GATE` (live) |
| License | **ODC-BY 1.0** at dataset level (incl. `citations` → contexts+intents). **Full-text follows source-paper license** (s2orc_v2 has per-paper `disclaimer` + `oaInfo.license`) | `S2-LIC`,`S2ORC` |
| Rate limits | Unauthenticated **1000 req/s shared** (throttled in practice; keyless 429s common); keyed introductory **1 RPS** (higher by request) | `S2-RATE` |
| Sizes | s2orc **10M** records / 30×4 GB; s2orc_v2 **16M** / 30×6 GB | `S2ORC` |

**Role:** the only route to **citation-context sentences** (Design C) and a large full-text corpus. **Two caveats:** (a) free-API context coverage is too sparse to assess at scale — the bulk `citations` dataset (ODC-BY, **redepositable with attribution**) or S2ORC (key-gated) is the real route; (b) redepositing full-text *extracts* is bounded by each source paper's license, not by ODC-BY.

### 1.5 PubMed / PMC OA — biomedical full text (retraction-rich)

| Property | Finding | Evidence |
|---|---|---|
| `Retracted Publication`[pt] | **33,173** | `PM-TOTAL` (live) |
| `Retraction Notice`[pt] | **32,272** | `PM-TOTAL` (live) |
| Per-year (by *original* pub-year) | 2010 703 · 2014 1,276 · 2016 1,316 · 2018 2,194 · 2020 2,838 · **2022 6,974** · 2023 2,128 · 2024 1,993 | `PM-YEAR` (live) |
| PMC OA subset size | **7,998,830** articles (2,285,811 with PDF) | `PMC-OA-COUNT` (live) |
| **PMID→PMCID linkage (retracted sample)** | **5/12** resolve to a PMCID (i.e., in PMC full text); high-profile *Lancet*/NEJM/*Nature* retractions largely **not** in the OA subset | `PMC-IDCONV` (live) |
| E-utilities limits | **3 req/s** no key, **10 req/s** with key; `tool`+`email` must be **registered** (not just supplied); large jobs off-peak | `PM-RATE` |
| PMC OA license tiers | Commercial (CC0/CC BY/BY-SA/BY-ND) · Non-Commercial (CC BY-NC/NC-SA/NC-ND) · **Other** (no machine-readable license; distribution limited) | `PMC-LIC` |
| Bulk route | `s3://pmc-oa-opendata` (us-east-1, `--no-sign-request`); JATS XML + plain text + PDF; per-article JSON incl. **`is_retracted`**, `license_code` | `PMC-BULK` |
| **2026 change** | 2026-04-13 legacy → deprecated prefix; **August 2026 `oa.fcgi` + legacy FTP removed**; new route = PMC Cloud Service by `PMCID.version` | `PMC-DEPREC` |
| Retraction pub-types | `Retracted Publication`[pt] (the article) vs `Retraction Notice`[pt] (the notice); tags `hasretractionin`/`hasretractionof`. Brief's "Retraction of Publication" is the **old** name. | `PM-PTYPE` |

**Role:** the richest *full-text* source for retraction precursors — but only for the **OA subset**, and high-profile retractions skew paywalled. `is_retracted` in the per-article JSON gives an in-corpus target flag.

### 1.6 OpenCitations — open citation links

| Property | Finding | Evidence |
|---|---|---|
| Citation counts (sample) | Surgisphere *Lancet* **7,475** · NEJM **3,689** · BMJ ordinary **20,090** — `doi:` join resolves | `OC-CCOUNT` (live) |
| `/citations/` list endpoint | **Unreliable today:** truncated chunked responses (`IncompleteRead`) on both urllib and requests, even for a small DOI → **use the dump, not the list API** | `OC-FIELDS` (live) |
| License | **CC0** ("freely reused for any purpose, incl. commercial"); free optional access token | `OC-LIC` |
| Index | COCI folded into unified **OpenCitations Index** (`/coci` → 404); multi-source (omid/doi/openalex/pmid); Jan 2026 dump 129 M+ entities | `OC-INDEX` |
| Fields | `oci,citing,cited,creation,timespan,journal_sc,author_sc` — **no citation contexts/snippets** | `OC-INDEX` |
| Rate limit | No numeric limit published — **UNVERIFIED** | `OC-INDEX` |

**Role:** a CC0 citation-link layer with self-citation flags (`journal_sc`/`author_sc`) and citation timespans — useful as an OpenAlex/Crossref cross-check for reference-structure precursors, **not** for citation contexts.

### 1.7 Replication-outcome datasets (Design B)

| Dataset | N (labeled pairs) | License | DOI join | Route | Evidence |
|---|---|---|---|---|---|
| **FReD / FLoRA** | FLoRA **2,404** papers (2026-07-13, living); FReD effect-level ~2–3k | **CC-BY 4.0** | ✅ `doi_o`+`doi_r` (strong) | OSF `9r62x`, GitHub `forrtproject/FReD-data`, R pkg | `REP-FRED` |
| **SCORE** | **164** replication pairs (49% replicated) | CC0 | ❓ likely (codebook **UNVERIFIED**) | OSF `dtzx4` | `REP-POOL` |
| **RPP** | **100** (97 full) | CC0 | ❌ **no DOI** (manual enrich) | GitHub `CenterForOpenScience/rpp` | `REP-POOL` |
| **Many Labs 1/2** | 13 / 28 effects | CC0 | ⚠️ name-only | OSF `wx7ck`/`8cd4r` | `REP-POOL` |
| replicationdatabase.com | — | — | — | **DEAD (DNS failure)** | `REP-POOL` |

Outcome labels are real (`replication_outcome ∈ {Success, Failure, Failure (reversal), …}` in FReD; p<.05-same-direction in RPP/SCORE), but coding is **heterogeneous/subjective** and FReD **aggregates** RPP/ML/RRRs → naïve pooling double-counts. **Cleaned unique N ≈ 1,200–1,800**, psychology-dominated.

### 1.8 arXiv — linkage layer only (per brief)

Confirmed **not** relevant as a target corpus here: **0/12** sample retracted papers carry an arXiv ID (`S2-LOOKUP`) — the retraction/replication universe is biomedical/social-science. arXiv remains the linkage substrate for **Design C** (the predecessor program's math case list). Access facts inherited & re-usable from the predecessor program (OAI-PMH `export.arxiv.org/oai2`, 3 s rate limit, metadata CC0) — not re-probed this phase.

---

## 2. R2 deep-dive — cross-source event dates & counts (the retrodiction-critical requirement)

**Count divergence (all live):**

| Source | Retraction count | Scope | Has event date? |
|---|---|---|---|
| OpenAlex `is_retracted` | **115,496** | all fields | ❌ flag only (no retraction date) |
| Crossref `update-type:retraction` | **73,501** | Crossmark depositors | ✅ day-level, typed (`updated-by`) |
| Retraction Watch true-`Retraction` | **65,598** | RW-curated, all fields | ✅ day-level (`RetractionDate`) + original date + reason |
| PubMed `Retracted Publication`[pt] | **33,173** | biomedical | ✅ (via linked notice) |

**Date spot check (11/12 sample DOIs found in RW; `RW-R2SPOT` + `CR-C`):**

| Case | RW `RetractionDate` | Crossref `updated-by` | Agreement |
|---|---|---|---|
| Wakefield 1998 (`…6736(97)11096-0`) | 2010-02-06, Retraction | retraction 2010-02-06 | ✅ **exact** |
| Gautret 2020 (`…2020.105949`) | 2020-04-11, **Expression of concern** | retraction **2024-12-16** (+ EoC) | ⚠️ *which-event* mismatch (EoC vs later retraction) |
| Surgisphere *Lancet* 2020 (`…6736(20)30367-6`) | **not found** by OriginalPaperDOI | `updated-by:2` (retraction present) | ⚠️ RW DOI-join miss (≈ the 3.8% incompleteness) |
| Hwang *Science* 2004 (`…science.1097243`) | 2007-10-26 | EoC 2006-era + later | ⚠️ curated-date differs from publisher notice |

**R2 conclusions:** (a) date **precision is day-level and adequate**; (b) the hard problem is **definitional** — expression-of-concern vs partial vs full retraction, and *which* date counts; (c) sources **disagree on membership** (~8% DOI-join miss even on famous cases) and on **counts** (1.75×). **Mandatory pre-registration item:** pin one authoritative event source (recommended: Retraction Watch), one `RetractionNature` inclusion rule (recommended: `Retraction` only, EoC/Correction excluded or analyzed separately), and one date field, with a Crossref `source`-field sensitivity arm.

---

## 3. Feasibility matrix — designs × requirements

Legend: **PASS** / **MARGINAL** / **FAIL** / **UNVERIFIED**, each with one-line evidence.

### Design A — Retraction precursors (events + metadata + contexts + controls)

| Req | Verdict | Evidence |
|---|---|---|
| R1 sanctioned access | **PASS** | OpenAlex CC0 snapshot, Crossref facts, RW CC0, PMC OA S3, S2 ODC-BY — all documented bulk/API routes, no scraping (`OA-BULK`,`CR-BULK`,`RW-ROUTE`,`PMC-BULK`,`S2ORC`) |
| R2 ground-truth events | **PASS** (with caveat) | RW day-level `RetractionDate`+`Nature`+`Reason`, Crossref typed `updated-by`; caveat = count/definition divergence (§2) |
| R3 background feasibility | **PASS** | retracted 115,496 vs 319.5 M works ⇒ background ≈ **2,766×**; per-year background (millions) ≫ retractions (~18k) (`OA-B`,`OA-A`,`OA-C`) |
| R4 coverage floor (≥50/stratum) | **PASS** | ≥1,000 retractions/yr since 2013; ≥8k/yr 2020+; even large per-field strata clear 50 (`OA-C`,`RW-ANALYZE`,`PM-YEAR`) |
| R5 licensing / redeposit | **MARGINAL** | metadata CC0/ODC-BY redepositable; **full-text extracts** bounded by per-paper license; abstracts copyright (`OA-LIC`,`S2ORC`,`PMC-LIC`,`CR-LIC`) |
| R6 linkage (join keys real) | **PASS** metadata / **MARGINAL** full-text | RW OriginalPaperDOI 96.2%, OpenAlex DOI 30/30; **but PMID→PMCID only 5/12** and S2 contexts sparse ⇒ full-text join for the retracted set is partial (`RW-ANALYZE`,`OA-E`,`PMC-IDCONV`,`S2-CONTEXTS2`) |

**Design A overall: STRONGEST.** Reference-structure / metadata / citation-count precursors are fully powered; *semantic/context* precursors are bounded by full-text coverage of the retracted set.

### Design B — Replication-signal calibration (outcomes + metadata + text)

| Req | Verdict | Evidence |
|---|---|---|
| R1 sanctioned access | **PASS** | FReD CC-BY, SCORE/RPP CC0 on OSF/GitHub, R package (`REP-FRED`,`REP-POOL`) |
| R2 ground-truth events | **MARGINAL** | outcomes exist (Success/Failure) but "events with reliable dates" are weak — replication *publication* date, heterogeneous subjective coding (`REP-FRED`) |
| R3 background feasibility | **MARGINAL/FAIL** | the replication SET is tiny & curated (non-random); a "strictly broader background" exists only as all-published-psych via metadata join, but matched-null/placebo from it is awkward at this target size (`REP-POOL`) |
| R4 coverage floor | **FAIL for temporal strata** | cleaned unique **N ≈ 1,200–1,800** total; per-year ≪ 50 (psych-dominated, clustered 2011+) — OK only as one pooled cross-section (`REP-POOL`) |
| R5 licensing / redeposit | **PASS** | CC-BY/CC0 redepositable to Zenodo (`REP-FRED`,`REP-POOL`) |
| R6 linkage | **PASS** (FReD) / **MARGINAL** (RPP no-DOI; SCORE unverified) | FReD `doi_o`+`doi_r`; RPP needs ~2h manual DOI enrichment (`REP-FRED`,`REP-POOL`) |

**Design B overall: FEASIBLE ONLY AS A POOLED CROSS-SECTION** — it does not satisfy the program's temporal/pre-registered-retrodiction R4 posture. Different shape from A/C.

### Design C — Method-import detection in citation contexts (full text + prior case list)

| Req | Verdict | Evidence |
|---|---|---|
| R1 sanctioned access | **PASS** | S2ORC (key, ODC-BY), PMC OA S3, OpenCitations CC0 (`S2ORC`,`PMC-BULK`,`OC-LIC`) |
| R2 ground-truth events | **MARGINAL** | "events" = the predecessor program's dated fusion catalysts (arXiv, verified) — small set (5 cases), not a large event corpus |
| R3 background feasibility | **PASS** | full-text corpora huge (S2ORC 16 M, PMC 8 M) (`S2ORC`,`PMC-OA-COUNT`) |
| R4 coverage floor | **MARGINAL/UNVERIFIED** | citation-context coverage measured **sparse** on free API (0–5/50); true coverage needs the S2ORC/`citations` bulk set; the case set itself is small (`S2-CONTEXTS2`) |
| R5 licensing / redeposit | **PASS** (S2 contexts, ODC-BY) / **MARGINAL** (PMC/S2ORC full-text extracts follow source license) | `S2-LIC`,`S2ORC`,`PMC-LIC` |
| R6 linkage | **MARGINAL** | arXiv IDs present in S2 for the math domain; but free-API context coverage sparse; S2ORC full text key-gated (`S2ORC-GATE`,`S2-CONTEXTS2`) |

**Design C overall: EXPLORATORY.** Viable via the ODC-BY `citations`/S2ORC bulk sets, but coverage is the open empirical question and the anchor event set is small.

---

## 4. Risk register (top 5 per viable design)

### Design A (retraction precursors) — recommended primary
1. **Full-text scarcity on the retracted set** (measured 5/12 PMC, 47% OA abstracts). *Mitigation:* scope the semantic/context arm to the OA-covered subset; treat reference-structure/citation precursors (fully covered) as primary; pre-declare the full-text subset as a secondary stratum.
2. **Retraction-date ambiguity** (EoC vs partial vs full; publisher vs RW date; §2). *Mitigation:* pin RW `Retraction`-only + one date field; Crossref `source` sensitivity arm.
3. **Curation/temporal bias in the event series** (2010–11 backfill, 2023 Hindawi spike). *Mitigation:* stratify by year/publisher; exclude or separately model mass-retraction batches; matched controls within the same journal-year.
4. **Control-matching confounds** — retracted papers differ systematically (topic, journal, productivity). *Mitigation:* matched-null on journal × year × field × citation-band drawn from the OpenAlex background (R3 headroom is ample, ~2,766×).
5. **Access-model drift** (OpenAlex freemium; PMC `oa.fcgi` removal Aug 2026). *Mitigation:* build on the **free CC0 snapshot** + `s3://pmc-oa-opendata`, not the metered/legacy APIs; pin snapshot release IDs.

### Design B (replication calibration) — secondary/pooled
1. **Underpowered temporal strata** (N≪50/yr). *Mitigation:* pre-register as a single pooled analysis, no yearly retrodiction.
2. **Aggregation double-counting** (FReD subsumes RPP/ML). *Mitigation:* dedupe on `doi_o`; treat FReD as the frame, add only non-overlapping SCORE.
3. **Heterogeneous/subjective outcome coding.** *Mitigation:* restrict to explicit `Success/Failure`, use `outcome_quote`, pre-declare the mapping.
4. **Domain narrowness (psychology).** *Mitigation:* scope claims to psych/social; SCORE adds breadth but only 164.
5. **Living-database drift** (FLoRA +114% in 4 months). *Mitigation:* pin an OSF version/SHA at lock.

---

## 5. Recommendation

> *Reasoning below; all supporting numbers are in §§1–3 with `probe_id`s.*

**Lead with Design A (retraction precursors), built on OpenAlex (backbone/background) + Retraction Watch (events) + Crossref (typed events/references), with a full-text precursor arm scoped to the PMC-OA / S2ORC-covered subset.** Rationale: it is the only candidate that clears R1–R4 decisively (sanctioned CC0/ODC-BY bulk routes; day-level typed events; a background ~2,766× the target; thousands of events per stratum), and its one soft requirement — R6/R5 for *full text* — is a **scoping** problem (analyze the covered subset, and lean on reference-structure/citation-context precursors) rather than a blocker. The predecessor program's guard cascade (matched-random nulls, coherence controls, non-stationarity guards, pre-registered informativeness floors) transfers directly: retracted vs matched-non-retracted is the same structural problem as fusion vs background, with a *much* larger and better-dated event set than any arXiv case.

**Hold Design B as a secondary, explicitly pooled study** — a pre-registered re-test of published replication predictors on FReD+SCORE. It is clean and cheap but cannot carry the program's temporal-retrodiction posture (R4 fails per-stratum); position it as a companion, not the flagship.

**Treat Design C as exploratory follow-on** — it reuses the predecessor's case list and needs the ODC-BY `citations`/S2ORC bulk sets (a free API key) before its coverage can even be assessed; the free-API context sparsity (0–5/50) says "measure coverage first, design second."

### Open judgment calls (reserved for the operator)
1. **Event authority + inclusion rule** — Retraction Watch `Retraction`-only (recommended) vs OpenAlex `is_retracted` vs Crossref; how to treat expressions of concern, partial retractions, corrections. This single choice moves the count by 1.75× (§2).
2. **Full-text scope for Design A** — restrict to PMC-OA (clean license, but ~40% of retracted-sample coverage and biomedical-skewed), add S2ORC (key + per-paper license diligence), or run a metadata/citation-only design (no full text) as the primary and full-text as secondary.
3. **Retraction-date semantics** — notice date vs original-publication date vs discovery; how to handle the 2010–11 backfill and 2023 mass-retraction batches (exclude, or model as strata).
4. **API key posture** — obtain a free OpenAlex key ($1/day budget) and S2 key (S2ORC + higher RPS), or stay entirely on the free CC0 snapshots to avoid metering. Affects reproducibility and cost.
5. **Redeposit boundary (R5)** — embeddings/derived features from CC0/ODC-BY sources redeposit freely; **full-text-derived extracts (citing sentences, span excerpts) must inherit each source paper's license** — decide whether the deposit ships derived features only.
6. **Design-B unit & version pin** — effect-level vs paper-level, and which FLoRA/FReD snapshot (living DB) to freeze.
7. **Production contact email** — replace the `recon@example.org` placeholder and complete NCBI `tool`/`email` registration before any harvest.

---

## 6. Provenance & appendix

- **`probe_log.jsonl`** — 93 entries. Live probes (`OA-*`, `CR-*`, `RW-*`, `S2-*`, `S2ORC-*`, `PM-*`, `PMC-*`, `OC-*`) each carry endpoint, params, HTTP status, and a result summary. Documentation reads (`*-LIC`, `*-RATE`, `*-BULK`, `REP-*`, etc., `status="doc_read(agent)"`) each cite the live-fetched source URL (2026-07-14).
- **`sample_records.json`** — 12 retracted + 12 ordinary works (OpenAlex-drawn) with DOI/PMID/PMCID/year — the cross-source join fixture reused across Crossref, RW, S2, PMC, OpenCitations spot checks.
- **`retraction_watch.csv`** — 65 MB, one-time bulk-route confirmation (the only route to `RetractionNature`+`Reason`+dual dates); parsed in-place, not redistributed.
- **Bot-blocked / unverified this phase:** OpenCitations `/citations/` list endpoint (chunked-read failures — use the dump); S2 Swagger docs (JS-gated — confirmed via machine-readable datasets API instead); SCORE/RPP OSF file listings (JS-gated / auth — confirmed public via OSF API); OpenAlex old rate-limit page (301 → JS Wayback only; current `developers.openalex.org` used instead). All flagged inline.

*End of report. Write-and-stop: no pipeline design, preregistration, or QSS follow-up initiated.*

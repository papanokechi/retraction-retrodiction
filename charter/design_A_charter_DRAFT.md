# Design-A Program Charter — Retraction-Precursor Retrodiction
### (DRAFT — §7 folded to binding; staged for final lock, not locked)

**Status:** DRAFT → operator review → lock. **Not locked. No build started.** (August clock; today 2026-07-14.) **JC8/§7 control matching RESOLVED and folded to binding (operator, 2026-07-14);** remaining lock gates are the §13 operator actions (JC7 contact/registration, snapshot pins, repo) + the August clock + operator's word.
**Program:** retrodiction-calibrated research-integrity / meta-science study, Design A (retraction precursors).
**Predecessor (inherited discipline):** arXiv fusion retrodiction, DOI [10.5281/zenodo.21334050](https://doi.org/10.5281/zenodo.21334050).
**Author of record:** Papanokechi (ORCID 0009-0000-6192-8273).
**Evidence base:** `datasets_scouting_report.md` + `probe_log.jsonl` (95 probes, 2026-07-14). Every empirical claim below carries a `probe_id`.

> **How to read this charter.** It is the program spine — the August analogue of the predecessor's case-selection pre-registration. It fixes sources, event definition, date semantics, strata, the observables hierarchy, the inherited guard cascade, and the redeposit boundary. It does **not** replace the per-observable locked YAML pre-registrations: each verdict-bearing observable gets its own machine-readable, timestamped lock **before any score is computed** (inheriting methods-paper §4.1). §7 control matching — previously the one open design call — is now **resolved and binding** (operator, 2026-07-14); the only items still open are the **§13 operator actions** (JC7, snapshot pins, repo).

---

## 0. The retrodiction question

> *Do papers that are later retracted exhibit, in the window strictly before their retraction notice, structural anomalies — in reference-list composition, citation dynamics, and (secondarily) abstract/full-text semantics — that separate them from matched non-retracted controls drawn from a strictly broader background, under a decision rule fixed before any similarity or anomaly score is computed?*

The predecessor answered the fusion analogue with a verdict-grade **null**. This program inherits the same posture: a pre-committed decision rule, a guard cascade running prophylactically, and a decomposition shipped with every verdict — so that whatever the sign of the result, it is trustworthy. **The retraction corpus is a better-sized instrument for the question than the fusion corpus was** (§1).

---

## 1. Design decision, scope, and the resolved judgment calls

**Primary: Design A.** It is the only candidate clearing R1–R4 decisively — sanctioned CC0/ODC-BY bulk routes (R1); day-level typed events (R2); background ≈ **2,766×** the target (R3, `OA-A`/`OA-B`); thousands of events per year-stratum (R4, `OA-C`/`RW-YEAR`). Its one soft requirement — full-text coverage of the retracted set (R5/R6) — is handled by **scoping** (§6), not treated as a blocker.

**Companion, deferred: Design B** (replication calibration) — a pooled cross-section on FReD+SCORE; does **not** start until A's pipeline runs (JC6, §12).

**Exploratory, gated: Design C** (method-import in citation contexts) — deferred behind an S2ORC coverage-measurement probe; not in the August charter.

**Resolved judgment calls (operator, 2026-07-14), carried into the sections named:**

| JC | Resolution | Section |
|---|---|---|
| JC1 event authority | Retraction Watch, `RetractionNature == "Retraction"` only; EoC/partial/correction excluded from primary, retained as separate stratum; Crossref `source`-field sensitivity arm approved | §3, §11 |
| JC2 full-text scope | Metadata/citation-structure **primary**; full-text semantic arm **secondary** with a coverage precondition; S2ORC deferred to a coverage probe | §6 |
| JC3 date semantics | `RetractionDate` = event-membership cutoff; `OriginalPaperDate` anchors the pre-window; two spikes get opposite treatments (§5) | §4, §5 |
| JC4 key posture | Snapshots are the reproducibility substrate; API keys are dev convenience only; no verdict-bearing quantity may depend on a metered endpoint | §2, §9 |
| JC5 redeposit boundary | Derived features only; no full-text span excerpts in the deposit | §10 |
| JC6 Design B | Paper-level unit, FReD frame deduped on `doi_o`, SCORE added non-overlapping, FLoRA pinned by OSF version+SHA; sequenced after A | §12 |
| JC7 contact/registration | Operator action — real email into polite pools + registered NCBI tool/email; **flag stays OPEN** | §13 |
| JC8 control matching | **RESOLVED (binding):** three-arm design — **C (pre-window citation match) primary · D (modeled covariate) co-primary sensitivity · A (no citation term) third arm**; **B (citations-to-date band) rejected** (conditions on collider); one pre-declared concordance rule; mandatory negative-control arm drawn from 2023 mass-retraction venues' non-retracted papers | §7 |

---

## 2. Pinned sources (the reproducibility substrate)

**Rule (JC4):** the program freezes against **CC0/ODC-BY bulk snapshots**, not metered APIs. Every verdict must be reproducible from the pinned snapshots alone. API keys (OpenAlex free tier, S2) are permitted for the development loop and the S2ORC coverage probe **only**.

| Layer | Source | Route (sanctioned, R1) | License (R5) | Pin at lock |
|---|---|---|---|---|
| Backbone / background / target flag | **OpenAlex** works+authors | `s3://openalex … --no-sign-request` (free), quarterly (`OA-BULK`) | **CC0** (`OA-LIC`) | → `snapshot_pins.yaml` `sources.openalex.snapshot_release_id` (+`release_notes_sha256`); dry-run 2026-07-14 = **2026-06-25** |
| Event layer (primary) | **Retraction Watch** (via Crossref) | GitLab `crossref/retraction-watch-data` CSV, daily (`RW-ROUTE`) | **CC0** (`RW-FIELDS`) | → `sources.retraction_watch.{csv_date,row_count,sha256}`; recon copy 2026-07-14 = 71,027 rows / 65,073,315 B (`RW-ANALYZE`) |
| Typed events / references / sensitivity | **Crossref** public data file | Academic Torrents `doi.org/10.13003/…` + AWS reqpays (`CR-BULK`) | metadata **CC0**; abstracts copyright (`CR-LIC`) | → `sources.crossref.{public_data_file_year,torrent_doi}`; dry-run = **2026** file (≈180 M records, through Mar 2026) |
| Full-text (secondary, biomedical) | **PMC OA subset** | `s3://pmc-oa-opendata … --no-sign-request` (`PMC-BULK`) | per-article `license_code` (Commercial/NC/Other) (`PMC-LIC`) | → `sources.pmc_oa.pmc_ids_last_modified` (+`bucket`); dry-run = `PMC-ids.csv.gz` 2026-07-13 |
| Citation links (cross-check) | **OpenCitations** Index dump | dump download (`OC-INDEX`) — **not** the `/citations/` list API (`OC-FIELDS` transport failures) | **CC0** (`OC-LIC`) | → `sources.opencitations.latest_index_dump`; dry-run = **January 2026** |
| Full-text (deferred, coverage-gated) | **S2ORC** | Datasets API + free key (`S2ORC`) | ODC-BY dataset; per-paper source license | not pinned this charter — coverage probe first |

**Pinning is mechanical (Gate 3).** On lock day, after Gate 1 (`config/contact.yaml`) is set, run `python scripts/pin_snapshots.py --pin` → it fetches each source fresh (including a fresh Retraction Watch CSV, recording `csv_date` + `row_count` + `sha256`) and writes **`charter/snapshot_pins.yaml`**. Every `→ sources.*` reference above resolves to a key in that file. A read-only **dry-run on 2026-07-14 confirmed all five lookups live** (`scripts/pin_snapshots.py --dry-run`; see WALKTHROUGH.md Gate 3). No snapshot identity is frozen until the `--pin` run on the operator's word.

**⚠️ Access-model changes inside the program window — both designed around:** OpenAlex has moved to a freemium API-key model (`OA-RATE`) — mitigated by using the free CC0 snapshot; PMC removes `oa.fcgi` + legacy FTP in **August 2026** (`PMC-DEPREC`) — mitigated by using `s3://pmc-oa-opendata` by `PMCID.version` from the outset.

---

## 3. Event definition & inclusion rule (JC1)

**Primary event set:** Retraction Watch records with **`RetractionNature == "Retraction"`** (strict). Count at recon: **65,598** (`RW-ANALYZE`). Rationale: RW is the only source carrying typed nature + controlled-vocabulary `Reason` + dual dates + both DOIs/PMIDs, with OriginalPaperDOI completeness **96.2%** (`RW-ANALYZE`) — the join key R6 depends on.

**Excluded from primary, retained as a pre-declared separate stratum:** Expressions of Concern (3,580), Corrections (1,490), Reinstatements (160), blank (199) (`RW-ANALYZE`). Justification is the **Gautret case** from the spot check — EoC 2020-04-11 vs later retraction 2024-12-16 (`RW-R2SPOT`/`CR-C`): EoCs are a distinct event class with different temporal semantics; poolable *never*, interesting *later*.

**Membership caveat (R2, measured):** sources disagree on both **count** (OpenAlex 115,496 / Crossref 73,501 / RW 65,598 / PubMed 33,173 — a ~1.75× spread, `OA-B`/`CR-B`/`RW-ANALYZE`/`PM-TOTAL`) and **membership** (Surgisphere *Lancet* is absent from RW by OriginalPaperDOI — the ~3.8% DOI-join miss, `RW-R2SPOT`). The charter pins **one** authority (RW) for the primary and treats the divergence as a sensitivity arm (§11), not as noise to smooth.

---

## 4. Date semantics (JC3) — with the backfill diagnostic resolved

- **Event-membership cutoff:** `RetractionDate` (the published-notice date — the only event date consistently observable; `RW-FIELDS`).
- **Pre-window anchor:** `OriginalPaperDate`. The retrodiction pre-window is defined *backward from the original publication forward to a fixed pre-notice horizon*, so the observables live in a period that exists independent of notice-date precision.

**Backfill diagnostic — RESOLVED, and it overturned the naive assumption (`RW-BACKFILL`, local parse of the cached CSV):**

| Cohort (by `RetractionDate`) | N | orig-date missing | notice→paper lag median | lag p90 | lag >10yr |
|---|---:|---:|---:|---:|---:|
| **2010–11 spike** | 9,945 | **0%** | **0 yr** | **1 yr** | 0.6% |
| 2018–19 normal | 5,433 | 0% | 2 yr | 8 yr | 6.2% |

The 2010–11 spike is **not** a backfill of genuinely old retractions (the hypothesis on the table). Original-paper dates are fully present and plausibly spread, but the notice→paper lag is **degenerate (median 0 yr)** — 90% of these papers were "retracted" the same year they were published, which is inconsistent with individually-investigated retraction timing (contrast the realistic 2018–19 median of 2 yr / p90 8 yr). This is diagnostic of **imputed/placeholder notice dates** from RW's 2010 founding-era cataloguing, not of rapid retraction.

**Ruling (charter-binding):** keep the 2010–11 papers in the **event set** (membership and `OriginalPaperDate` are reliable — 0% missing), but **exclude pre-2012 `RetractionDate` values from any time-of-retraction (timing) analysis.** The pre-window anchors on `OriginalPaperDate`, which the diagnostic confirms is sound for this cohort. *(This is precisely the artifact-caught-in-the-act pattern the predecessor program was built to surface — logged, dated, and carried into the design.)*

---

## 5. Strata (JC3)

1. **Primary stratum:** individually-investigated `Retraction` events, 2012 onward (post-imputation-artifact window per §4), matched controls within journal × year × field.
2. **Mass-retraction stratum (excluded from primary, pre-declared separate):** the **2023 spike (13,204 by `RetractionDate`, `RW-YEAR`)** — the Hindawi/IEEE paper-mill wave. Batch events with a single detection mechanism (paper-mill screening) mix a different generating process; pooled with fraud-investigation retractions they contaminate the null (see guard #8, §8). Separated, the **between-stratum** comparison — *do paper-mill products look anomalous earlier than fraud-investigation retractions?* — is itself a first-class question.
3. **Pre-2012 membership-only stratum:** the 2010–11 imputed-date cohort (§4) — usable for prevalence/membership analyses, excluded from timing.
4. **EoC / correction stratum:** §3 — separate event class, not pooled.

Per-year primary-stratum sizes clear R4's 50-floor by orders of magnitude (2018 2,527 · 2022 5,564 · 2024 6,135, `RW-YEAR`), leaving ample headroom even under fine field × year stratification.

---

## 6. Observables hierarchy (JC2)

**Design principle (binding):** the verdict-bearing observables are the **fully-covered, harder-to-fake** ones. A paper's bibliography is fixed at publication and cannot be retrofitted; abstract semantics can correlate with topic confounds. So the primary observable is also the more defensible one.

**Tier 1 — PRIMARY (metadata + citation structure; ~full coverage on the retracted set):**
- Reference-list structure (size, age distribution, self-citation share, reference concentration) — OpenAlex `referenced_works` present **30/30** on the retracted sample (`OA-E`).
- Citation dynamics pre-notice (accrual curve, velocity, citing-venue diversity) — OpenCitations `journal_sc`/`author_sc` self-citation flags + timespans (`OC-INDEX`); OpenAlex/Crossref cross-check.
- Metadata trajectories (author count, affiliation churn, venue).

**Tier 2 — SECONDARY (semantic; coverage-gated):**
- Abstract-semantic anomalies — but OpenAlex abstract coverage on retracted works is **47% (14/30, `OA-E`)**; run only where present.
- Full-text semantic/structural precursors on the **PMC-OA-covered subset** — measured coverage **5/12 sample (`PMC-IDCONV`)**, biomedical-skewed. **Coverage precondition (finding-7 family):** the covered subset must clear the R4 floor **per stratum**, checked *before* any embedding is computed; if it fails, the semantic arm is reported as coverage-limited, not as a null.

**Tier 3 — DEFERRED:** S2ORC full text / citation contexts — free-API context coverage measured **sparse (0–5/50, `S2-CONTEXTS2`)**; requires a key + a dedicated coverage-measurement probe before any design commitment (Design-C lesson applied preemptively: measure coverage first, design second).

---

## 7. Control matching — RESOLVED, BINDING (JC8, operator 2026-07-14)

*This is the single most attackable design choice in the study. It is resolved here into a three-arm design with a pre-declared concordance rule; the reasoning — including why one option was rejected — is itself locked field content, so the collider is disclosed, not buried.*

**The confound (collider risk):** retraction probability correlates with **visibility** — highly-cited, high-profile papers attract more scrutiny and are likelier to be investigated and retracted. Scrutiny therefore sits on the causal path between any real precursor signal and the retraction outcome; **matching on citations-to-date conditions on that collider**, and can *induce* a spurious association or mask a real one in either direction.

**Matching core (all arms):** journal × publication-year × field.

**Decision — three retained arms (no-handling / design-handling / model-handling), one rejected:**

| Arm | Role | Matching / handling | Locked rationale |
|---|---|---|---|
| **C** | **PRIMARY** | journal × year × field × **citations-as-of-the-pre-notice-horizon** | Uses only information that existed *before* the outcome process could contaminate it, weakening the collider path to whatever visibility↔scrutiny correlation already existed pre-investigation. The per-paper pre-horizon citation snapshot is **the same machinery Tier-1's citation-dynamics observable needs (§6)** — cost is shared, not additive. |
| **D** | **CO-PRIMARY SENSITIVITY** | journal × year × field; **citations entered as a modeled covariate** with a pre-declared sensitivity analysis | Trades a design assumption for a modeling assumption. Not primary — this program's aesthetic is that **design-time protection beats model-time correction** — but run alongside C to test robustness of the collider-handling choice. |
| **A** | **THIRD ARM** | journal × year × field, **no citation term** | The cheap no-handling baseline (a strict subset of the pipeline); completes the triangle. Leaves visibility uncontrolled — its divergence from C/D *localises* the visibility effect. |
| **B** | **REJECTED** | ~~journal × year × field × citations-to-date band~~ | **Rejected outright:** citations-to-date at matching time include *post-scrutiny* dynamics, which lie on the causal path between precursor and retraction — the textbook collider conditioning. Recorded in the locked field as rejected *with this reason*, not merely omitted. |

**Pre-declared concordance rule (locked before any score):** the headline is read across arms **A / C / D**. If **C-matched and D-modeled agree**, the finding is reported as **robust to collider-handling**. If they **diverge**, the divergence is not an embarrassment to be reconciled post hoc — it is the **finding-9-analogue this charter predicts will live here**, reported as such with the decomposition (§4.3) attached.

**C's residual caveat (pre-declared, not discovered later):** pre-window citation matching **weakens but does not eliminate** the collider — pre-window visibility still correlates with eventual scrutiny probability. The locked field states this residual explicitly; the A/C/D triangle is precisely what bounds its size.

**Negative-control arm (mandatory, sharpened):** draw controls specifically from the **2023 mass-retraction venues' *non-retracted* papers** — same journals, same years, having survived the paper-mill screening (§5 mass-retraction stratum). This is guard #4 (placebo contamination) in its Design-A form: **if the precursor score flags *those* papers too, the score is detecting venue pathology, not paper pathology** — and forcing that distinction into the open is exactly what the negative control is for.

**Required at lock:** the matching variables, the rejection of B *with its reason*, the concordance rule, C's residual caveat, and the negative-control source are pre-declared **in the same locked field** — the §7/Table-4 audit-trail principle the predecessor established (accountability via documented decision provenance).

---

## 8. Guard-cascade inheritance — Table 1 as a checklist

The predecessor's nine-artifact guard cascade (methods-paper §4.7, Table 1) is the transferable payload. Each guard is inherited and **re-instantiated for Design A**; each must be present *at conception* and run prophylactically (the condition under which a negative can be trusted). This block is the pre-run checklist.

| # | Inherited artifact class | Design-A instantiation (the guard, re-aimed) | ☐ |
|---|---|---|---|
| 1 | resolution floor | Strata & control sets are **pinned by explicit rule** (journal×year×field[×citation per §7]), never discovered by clustering; membership fixed in the lock | ☐ |
| 2 | ceiling saturation | Every percentile/anomaly statistic checked for **headroom** — a precursor score pinned at its ceiling carries no trend information | ☐ |
| 3 | pre-bridge anti-proximity → type hypothesis | The sign of a precursor is a **hypothesis about retraction *type*** (fraud vs honest-error vs paper-mill), not a single expected direction; a "more normal than controls" reading is admissible and typed | ☐ |
| 4 | placebo contamination | **Corpus-verified negative controls** — controls confirmed non-retracted *as of the pinned snapshot*, screened against later retraction; the §7 negative-control arm | ☐ |
| 5 | polysemous verdict | Any verdict string reachable by opposite mechanisms carries the **informativeness flag**; no bare cell | ☐ |
| 6 | saturation taxonomy (3-state) | Percentile precursors labeled **flat-at-random / saturated / informative**, never collapsed | ☐ |
| 7 | null infeasibility → broad-background precondition | **R3 check before scoring:** background pool strictly broader than the target set (measured ≈2,766×, `OA-B`/`OA-A`); the covered-subset floor of §6 is the same guard at full-text scale | ☐ |
| 8 | coherence geometry | **Coherence-matched null:** single-journal/batch retraction sets (esp. the 2023 Hindawi stratum, §5) can read anomalous from set geometry alone; the null must match set coherence, and unrelated placebos are the tell | ☐ |
| 9 | null non-stationarity | **Fixed-size stationary re-scoring:** citation and reference counts grow with time; any temporal precursor statistic must difference out the size/time non-stationarity (fixed-n subsampling), with the raw/null-mean/null-std/gap **decomposition shipped with every verdict** (§4.3 inherited) | ☐ |

**Inherited protocol invariants (methods-paper §4.1–4.6), binding here:**
- **Locked YAML per observable**, authored+timestamped+committed **before data**; changing a term/feature list is a *new* lock, not an edit; the lock enumerates every reachable verdict cell (the outcome map).
- **The locked cell stands verbatim**; interpretation is layered after, changing no locked field.
- **Matched-random null** (size-[and field-]matched draws, K per the §4.5–4.6 spec) with a **placebo-relative floor** `M = 2·SD(Δgap)` over the matched-null trajectories.
- **Non-spending separability/consistency checks** may inform framing but never enter the score.
- **A GO-precondition introduced conversationally mid-flight is junior to the lock** (the case-5 design principle).

### 8.1 Guard #3 pre-committed sign-by-stratum hypothesis table

*Guard #3 (§8, row 3) admits a "more normal than controls" reading as a **typed** result rather than a non-finding. The operator's sharpening, binding here: the interpretation of that cell is **pre-committed now**, before any score exists, so it can never become a post-hoc story. The table below is a **pre-registered directional hypothesis** (not a verdict); it is locked under the §8 invariants — revisable only by a **new** lock, never an edit. Signs are scored **per stratum**; pooling retraction types with opposite predicted signs would cancel — which is itself the reason the stratification (§5) is mandatory.*

Anomaly convention: **anomalous** = precursor differs from matched controls in the "suspicious" direction; **hyper-normal** = *more* regular than genuine controls (the guard-#3 tell); **at-null** = no pre-notice Tier-1 signal predicted (the honest hard case).

| Retraction type (stratum) | Reference-structure prediction (Tier-1) | Citation-dynamics prediction (Tier-1) | Net pre-committed sign | Mechanism |
|---|---|---|---|---|
| **Paper-mill / mass-fabrication** (2023 batch stratum, §5) | **Hyper-normal** — templated bibliographies: high reference concentration, homogeneous age distribution, *lower* variance than genuine controls | Low/flat pre-notice accrual; possible citation-ring self-citation (`journal_sc`/`author_sc`) | **HYPER-NORMAL** on structure (+ self-citation flag) | industrialized templates → conformity reads as excess regularity |
| **Individual data fabrication / falsification** (classic fraud) | At-null to **weakly anomalous** — the manipulation is in the *data*, not the bibliography | Possibly elevated later, but post-window; pre-window ~ near-null | **AT-NULL / weakly anomalous** (the honest hard case) | fabrication leaves little metadata trace before the notice |
| **Plagiarism / duplication** | **Anomalous** — copied or overlapping reference lists; high bibliographic similarity to a source | Near-null pre-notice | **ANOMALOUS** | bibliography is copied along with the text |
| **Honest error / irreproducibility** (correction-adjacent) | **At-null** — genuine papers; no pre-notice structural signal predicted | At-null | **AT-NULL** | error surfaces post hoc; the near-negative-control case |
| **Authorship / process / fake peer review** | Near-null on Tier-1 | Near-null on Tier-1 | **AT-NULL** on Tier-1 (signal, if any, sits in review metadata not covered by §2) | pathology is in the editorial process, not the artifact |

**Consequence for reading:** a single pooled "retracted vs control" precursor score is **pre-declared uninformative** by this table (the hyper-normal and anomalous strata cancel). The verdict-bearing comparisons are **within-type**, and the **paper-mill-vs-fraud contrast is a first-class prediction** (hyper-normal vs anomalous), not an afterthought. Every cell still passes through the informativeness guard (row 5) and ships its decomposition (row 9).

---

## 9. Access & reproducibility posture (JC4)

- Freeze against the pinned **CC0/ODC-BY snapshots** (§2). **No verdict-bearing quantity may depend on a metered endpoint.**
- Obtain the free OpenAlex key ($1/day tier, `OA-RATE`) and S2 key for the **development loop and the S2ORC coverage probe only**.
- **Rule:** *if the free snapshot cannot reproduce it, it is not in the paper.*
- Record the snapshot release-IDs (§2 checkboxes) in the run manifest and the Zenodo deposit.

---

## 10. Redeposit boundary (JC5)

- **Ships in the deposit (CC0/ODC-BY-derived, clean):** embeddings, extracted structural/citation features, the event table, match keys, and all code.
- **Does not ship:** full-text-derived span excerpts / citing sentences. The paper quotes at most what fair scholarly practice covers; the deposit **manifest states the boundary explicitly**.
- Effect: R5 collapses to a one-paragraph statement instead of a per-paper license audit.

---

## 11. Sensitivity arms

1. **Event-authority divergence (R2):** re-run the headline comparison with the OpenAlex `is_retracted` set and the Crossref `update-type:retraction` set; report verdict stability across the ~1.75× count spread (`OA-B`/`CR-B`/`RW-ANALYZE`).
2. **Crossref `source` field:** split events into publisher-asserted vs retraction-watch-asserted (`CR-UPD`) — the R2 analogue of the predecessor's §4.1 concordance arms.
3. **Stratum-membership sensitivity:** primary with/without the 2023 mass-retraction stratum (§5).

---

## 12. Design B — companion spec, deferred (JC6)

Unit **paper-level**; frame **FReD/FLoRA** (CC-BY, `doi_o`+`doi_r`, `REP-FRED`) deduped on `doi_o`; add **SCORE** (CC0, 164 pairs) only where non-overlapping; pin the **FLoRA snapshot by OSF version + SHA** at its own lock. Cleaned unique **N ≈ 1,200–1,800**, psychology-dominated (`REP-POOL`) → **single pooled cross-section only** (per-year strata fail R4). **Sequencing:** does not begin until Design A's pipeline is running; executable in a later gap week.

---

## 13. Open operator actions (before any production run)

1. **JC7 — contact/registration (OPEN — operator):** fill `config/contact.yaml` `contact_email` with a real address (the harness's Gate-1 guard refuses every network call until this is set — placeholder-proof), and, for higher PubMed/PMC throughput, create an NCBI API key (NCBI account → Settings → **API Key Management**) and paste it into `ncbi_api_key`. `tool`+`email` are self-declared (no separate registration). Step-by-step in **WALKTHROUGH.md Gate 1b**. *Flag stays open until operator confirms done.*
2. **JC8 — control matching (§7): RESOLVED & folded to binding (2026-07-14)** — three-arm design (C primary / D co-primary sensitivity / A third arm; B rejected), one concordance rule, negative control from 2023 mass-retraction venues. No longer open; recorded here for provenance.
3. **Snapshot pins (§2): mechanized (Gate 3) — operator runs at lock.** `python scripts/pin_snapshots.py --pin` writes `charter/snapshot_pins.yaml` (OpenAlex release-ID, fresh RW CSV date/rows/SHA-256, Crossref annual-file year+torrent DOI, PMC `PMC-ids.csv.gz` date, OpenCitations dump). Dry-run 2026-07-14 confirmed all five lookups live.
4. **Program home:** create the dedicated repo **before week one** — `papanokechi/retraction-retrodiction`, with **this charter + the recon evidence (`datasets_scouting_report.md`, `probe_log.jsonl`, probes) as the founding commit** (assembled locally in Gate 2a; push steps in WALKTHROUGH.md Gate 2b) — so this program never accrues the predecessor's "not a git repo" debt.

---

## 14. Sequence to lock, and the week-one build gate

**Draft (this document, §7 now binding) → operator completes §13 items (JC7 contact/registration, snapshot pins, repo) → lock the charter → per-observable YAML locks → week-one build.**

Week-one build (on the August clock, not before) is scoped exactly as the predecessor's: **harvest module + tests + manifests, written and green, before any question is asked of the data.** No similarity, no anomaly score, no verdict until the guard cascade (§8) is present at conception and the pre-registrations are locked.

Part 1 (QSS inquiry) stays quiet on its own track — no chaser. The two programs now run independently, which is the portfolio shape intended.

---

*End of DRAFT charter. Awaiting operator review — no lock, no preregistration YAML, and no build initiated.*

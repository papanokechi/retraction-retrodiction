# SPDX-License-Identifier: MIT
"""Append agent documentation-read findings to probe_log.jsonl as doc_read entries,
so every license/rate-limit/attribution claim in the report traces to a log line.
Source: three background research agents (research-agent doc reads, 2026-07-14),
each URL fetched live on 2026-07-14 (cited inline)."""
from probe import log_probe

DOC = "doc_read(agent)"

reads = [
 # OpenAlex
 ("openalex", "https://developers.openalex.org/", "LICENSE CC0 1.0 ('complete dataset is free under the CC0 license'); citation request Priem/Piwowar/Orr 2022 arXiv:2205.01833 (non-binding, CC0 => no legal attribution)", "OA-LIC"),
 ("openalex", "https://developers.openalex.org/api-reference/authentication", "2026 model change: polite-pool/mailto REPLACED by freemium API key. Free $0.10/day no key, $1/day free key; List+Filter $0.10/1k, Search $1/1k, singleton free; >100 req/s or over-budget => 429. Snapshot bulk download FREE.", "OA-RATE"),
 ("openalex", "https://developers.openalex.org/download/snapshot-format", "Bulk snapshot s3://openalex (CC0, --no-sign-request); gz JSONL ~330GB compressed / ~1.6TB decompressed; Parquet rolling out; quarterly (free) / daily (paid); entities incl works/authors/topics", "OA-BULK"),
 # Crossref
 ("crossref", "https://www.crossref.org/documentation/retrieve-metadata/", "License table: bibliographic metadata+references = facts/not-copyrightable; Crossref-generated = CC0; Open Funder Registry + Retraction Watch = CC0; Abstracts = publisher/author COPYRIGHT (not CC0)", "CR-LIC"),
 ("crossref", "https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/", "Rate limits eff. 2025-12-01: Public 5 req/s (single) /1 (list) conc 1; Polite (mailto) 10/s single /3 list conc 3; Plus 150/s. mailto recommended not required.", "CR-RATE"),
 ("crossref", "https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/", "Retractions in update-to field; RW updates flagged by source field = 'publisher' or 'retraction-watch'; 12 update-type values incl retraction/partial_retraction/withdrawal/removal/expression_of_concern/correction", "CR-UPD"),
 ("crossref", "https://www.crossref.org/documentation/retrieve-metadata/bulk-downloads/", "Annual public data file: JSONL tar, 2026 file 208GB compressed ~180M records; Academic Torrents doi.org/10.13003/nggf-vt1j + AWS requester-pays api-snapshots-reqpays-crossref (~$18)", "CR-BULK"),
 # Retraction Watch
 ("retraction_watch", "https://www.crossref.org/blog/news-crossref-and-retraction-watch/", "RW acquired by Crossref 2023-09-12 (DOI 10.13003/c23rw1d9), made public CC0. GitLab route added 2024-10-10. Acquisition-era count ~50k combined.", "RW-ACQ"),
 ("retraction_watch", "https://gitlab.com/crossref/retraction-watch-data", "Primary route: GitLab repo, CSV, updated every working day (README generated 2026-07-13). Labs API mirror api.labs.crossref.org/data/retractionwatch. No LICENSE file in repo (404); CC0 per Crossref docs.", "RW-ROUTE"),
 ("retraction_watch", "https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/", "20 fields incl RetractionDate/OriginalPaperDate (day-level MM/DD/YYYY 0:00), RetractionNature, Reason (controlled vocab), both DOIs + both PubMedIDs. Caveat: EoC/corrections 'not as comprehensive as retractions'; RetractionDate = notice date not misconduct date.", "RW-FIELDS"),
 # Semantic Scholar / S2ORC
 ("semantic_scholar", "https://www.semanticscholar.org/product/api", "Unauthenticated: 1000 req/s SHARED pool (throttled in practice); keyed introductory = 1 RPS/key, higher by request. Dataset download endpoints require API key.", "S2-RATE"),
 ("semantic_scholar", "https://api.semanticscholar.org/datasets/v1/release/latest", "License ODC-BY 1.0 for all S2AG datasets incl citations (contexts+intents). citations schema: isInfluential, contexts (text around citation), intents (intent classification, Cohan 2019).", "S2-LIC"),
 ("semantic_scholar", "https://github.com/allenai/s2orc", "S2ORC now only via Datasets API + free API key (x-api-key), pre-signed S3 URLs. Old standalone non-commercial; current ODC-BY 1.0 at DATASET level, but underlying full-text follows source paper license (s2orc_v2 has per-paper disclaimer + oaInfo.license). s2orc 10M/30x4GB; s2orc_v2 16M/30x6GB.", "S2ORC"),
 # PubMed / PMC
 ("pubmed", "https://www.ncbi.nlm.nih.gov/books/NBK25497/", "E-utilities: no key = 3 req/s; with key = 10 req/s (higher by request). tool+email must be REGISTERED (email eutils@ncbi.nlm.nih.gov); large jobs weekends/9pm-5am ET. Non-compliance => IP block.", "PM-RATE"),
 ("pmc", "https://pmc.ncbi.nlm.nih.gov/tools/openftlist/", "PMC OA Subset 3 license tiers: Commercial (CC0/CC BY/BY-SA/BY-ND), Non-Commercial (CC BY-NC/NC-SA/NC-ND), Other (no machine-readable license; distribution limited).", "PMC-LIC"),
 ("pmc", "https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/", "Bulk: AWS Open Data s3://pmc-oa-opendata (us-east-1, world-readable, --no-sign-request); JATS XML + plain text + PDF; per-article JSON incl is_retracted, license_code (CC BY/CC BY-NC/CC BY-NC-ND/TDM/null).", "PMC-BULK"),
 ("pmc", "https://pmc.ncbi.nlm.nih.gov/tools/oa-service/", "2026 CHANGE: 2026-04-13 legacy files moved to deprecated prefix; AUGUST 2026 oa.fcgi web service + legacy FTP removed; new primary route = PMC Cloud Service s3://pmc-oa-opendata by PMCID.version.", "PMC-DEPREC"),
 ("pubmed", "https://www.nlm.nih.gov/mesh/pubtypes.html", "'Retracted Publication'[pt] = the retracted article; 'Retraction Notice'[pt] = the notice (brief's 'Retraction of Publication' is the OLD name). Tags hasretractionin / hasretractionof.", "PM-PTYPE"),
 # OpenCitations
 ("opencitations", "https://opencitations.net/", "License CC0 ('freely reused for any purpose, including commercial'). Access token optional (authorization header), free.", "OC-LIC"),
 ("opencitations", "https://api.opencitations.net/index/v2", "COCI folded into unified OpenCitations Index (opencitations.net/coci => 404). Multi-source (omid/doi/openalex/pmid). Jan 2026 dump 129M+ entities. REST fields: oci, citing, cited, creation, timespan, journal_sc, author_sc. NO citation contexts/snippets. No numeric rate limit published (UNVERIFIED).", "OC-INDEX"),
 # Replication datasets
 ("replication", "https://osf.io/9r62x/ ; github.com/forrtproject/FReD-data", "FReD/FLoRA (FORRT Replication DB): FLoRA 2,404 papers (2026-07-13, living); FReD effect-level ~2-3k. CC-BY 4.0. Columns replication_outcome, doi_o, doi_r, es_o/r, p_o/r, author_overlap, outcome_quote => STRONG DOI join. Caveat: AGGREGATES RPP/ML/RRRs (double-count); psych-dominated.", "REP-FRED"),
 ("replication", "https://osf.io/dtzx4/ (SCORE) ; github.com/CenterForOpenScience/rpp (RPP) ; osf.io wx7ck/8cd4r (ML1/2)", "SCORE N=164 replication pairs (49% replicated), CC0, broad fields 2009-18, DOIs likely (codebook unverified). RPP N=100 (97 full), CC0, NO DOI column (manual enrich). Many Labs 1/2 = 13/28 effects, CC0, name-only join. replicationdatabase.com DEAD (DNS). Cleaned pooled unique N ~1,200-1,800 (FReD-dominated).", "REP-POOL"),
]

for ds, url, summary, pid in reads:
    log_probe(ds, url, summary, status=DOC, probe_id=pid,
              note="verbatim license/rate/coverage read via background research agent; URL fetched live 2026-07-14")
print(f"logged {len(reads)} doc_read entries")

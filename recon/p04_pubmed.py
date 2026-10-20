# SPDX-License-Identifier: MIT
"""PubMed E-utilities + PMC probes (read-only). Retraction counts, per-year, ID linkage."""
import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
from probe import get, log_probe, RECON_DIR, CONTACT_EMAIL, NCBI_TOOL

DS = "pubmed"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
COMMON = {"tool": NCBI_TOOL, "email": CONTACT_EMAIL, "retmode": "json"}

def esearch_count(term, extra=""):
    t = term + (f" AND {extra}" if extra else "")
    st, d, url = get(f"{EUTILS}/esearch.fcgi", params=dict(COMMON, db="pubmed", term=t, rettype="count"), sleep=1.0)
    cnt = None
    if st == 200 and isinstance(d, dict):
        cnt = int(d.get("esearchresult", {}).get("count", -1))
    return cnt, url

# A. totals for both retraction publication types
for term in ['"Retracted Publication"[pt]', '"Retraction Notice"[pt]']:
    cnt, url = esearch_count(term)
    log_probe(DS, url, f"esearch {term} total = {cnt:,}" if cnt is not None else f"{term} FAILED",
              status=200 if cnt is not None else None, result={"term": term, "count": cnt}, probe_id="PM-TOTAL")
    print(f"{term}: {cnt:,}" if cnt is not None else f"{term}: FAILED")

# B. per-year "Retracted Publication"[pt] (the retracted articles themselves), datetype=pdat
print("\n-- Retracted Publication[pt] per year --")
per_year = {}
for y in [2010, 2014, 2016, 2018, 2020, 2022, 2023, 2024]:
    cnt, url = esearch_count('"Retracted Publication"[pt]', extra=f'("{y}"[dp] : "{y}"[dp])')
    per_year[y] = cnt
    log_probe(DS, url, f"Retracted Publication[pt] {y} = {cnt}", status=200,
              result={"year": y, "count": cnt}, probe_id="PM-YEAR")
    print(f"  {y}: {cnt:,}" if cnt is not None else f"  {y}: FAILED")

# C. PMC OA subset count (still-live oa.fcgi; deprecating Aug 2026)
st, d, url = get("https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi", sleep=1.0, accept="text")
import re
m = re.search(r"<count>(\d+)</count>", d) if isinstance(d, str) else None
oa_count = int(m.group(1)) if m else None
log_probe("pmc", url, f"PMC OA subset article count = {oa_count:,}" if oa_count else "OA count parse failed",
          status=st, result={"oa_count": oa_count}, probe_id="PMC-OA-COUNT")
print(f"\nPMC OA subset count: {oa_count:,}" if oa_count else "\nPMC OA count: parse failed")

# D. PMID <-> DOI <-> PMCID linkage via idconv for the sample retracted papers (R6)
with open(os.path.join(RECON_DIR, "sample_records.json"), encoding="utf-8") as f:
    sample = json.load(f)
pmids = [str(r["pmid"]) for r in sample["retracted"] if r.get("pmid")][:12]
st, d, url = get("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/",
                 params={"ids": ",".join(pmids), "format": "json",
                         "tool": NCBI_TOOL, "email": CONTACT_EMAIL}, sleep=1.0)
if st == 200 and isinstance(d, dict):
    recs = d.get("records", [])
    with_pmcid = sum(1 for r in recs if r.get("pmcid"))
    with_doi = sum(1 for r in recs if r.get("doi"))
    log_probe("pmc", url, f"idconv: {len(recs)} PMIDs -> pmcid {with_pmcid}, doi {with_doi}",
              status=st, result={"n": len(recs), "with_pmcid": with_pmcid, "with_doi": with_doi,
                                 "sample": recs[:3]}, probe_id="PMC-IDCONV")
    print(f"\nidconv {len(recs)} PMIDs -> {with_pmcid} have PMCID (in PMC), {with_doi} have DOI")
else:
    log_probe("pmc", url, f"idconv failed ({st})", status=st, note=str(d)[:200], probe_id="PMC-IDCONV")
    print("\nidconv:", st, str(d)[:200])

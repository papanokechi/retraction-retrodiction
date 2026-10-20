# SPDX-License-Identifier: MIT
"""Semantic Scholar Graph API + S2ORC datasets route probe (read-only)."""
import json, os
from probe import get, log_probe, RECON_DIR

DS = "semantic_scholar"
G = "https://api.semanticscholar.org/graph/v1"
SLEEP = 1.3  # keyless pool ~1 req/s; be gentle

with open(os.path.join(RECON_DIR, "sample_records.json"), encoding="utf-8") as f:
    sample = json.load(f)

FIELDS = "externalIds,title,year,openAccessPdf,abstract,tldr,referenceCount,citationCount,isOpenAccess,s2FieldsOfStudy"

def lookup(rec, kind):
    doi = rec.get("doi")
    if not doi:
        return None
    st, d, url = get(f"{G}/paper/DOI:{doi}", params={"fields": FIELDS}, sleep=SLEEP)
    if st != 200 or not isinstance(d, dict):
        log_probe(DS, url, f"[{kind}] {doi} not resolved ({st})", status=st, probe_id="S2-LOOKUP")
        return {"doi": doi, "resolved": False}
    ext = d.get("externalIds") or {}
    info = {"doi": doi, "resolved": True, "has_arxiv": "ArXiv" in ext, "has_pmid": "PubMed" in ext,
            "has_abstract": bool(d.get("abstract")), "has_oa_pdf": bool(d.get("openAccessPdf")),
            "has_tldr": bool(d.get("tldr")), "refs": d.get("referenceCount"),
            "cites": d.get("citationCount")}
    log_probe(DS, url, f"[{kind}] {doi} arxiv={info['has_arxiv']} abstract={info['has_abstract']} oa_pdf={info['has_oa_pdf']} refs={info['refs']} cites={info['cites']}",
              status=st, result=info, probe_id="S2-LOOKUP")
    return info

print("--- S2 paper lookups (retracted) ---")
res = [lookup(r, "RETR") for r in sample["retracted"][:8]]
print("--- S2 paper lookups (ordinary) ---")
res += [lookup(r, "ORD") for r in sample["ordinary"][:4]]
ok = [r for r in res if r and r.get("resolved")]
agg = {"resolved": len(ok), "n": len(res),
       "with_abstract": sum(r["has_abstract"] for r in ok),
       "with_oa_pdf": sum(r["has_oa_pdf"] for r in ok),
       "with_arxiv": sum(r["has_arxiv"] for r in ok)}
log_probe(DS, "summary", f"S2 sample: {agg}", status="ok", result=agg, probe_id="S2-AGG")
print("AGG:", agg)

# Citation contexts/intents (Design C core): probe one well-cited retracted paper
probe_doi = sample["retracted"][0]["doi"]
st, d, url = get(f"{G}/paper/DOI:{probe_doi}/citations",
                 params={"fields": "contexts,intents,isInfluential", "limit": 10}, sleep=SLEEP)
if st == 200 and isinstance(d, dict):
    data = d.get("data", [])
    with_ctx = sum(1 for c in data if c.get("contexts"))
    with_int = sum(1 for c in data if c.get("intents"))
    example = next((c.get("contexts") for c in data if c.get("contexts")), None)
    log_probe(DS, url, f"citations n={len(data)} with_contexts={with_ctx} with_intents={with_int}",
              status=st, result={"n": len(data), "with_contexts": with_ctx, "with_intents": with_int,
                                 "example_context": (example or [None])[0]}, probe_id="S2-CONTEXTS")
    print(f"\ncitation contexts: {with_ctx}/{len(data)} have contexts, {with_int}/{len(data)} have intents")
    if example:
        print("example context:", str(example[0])[:200])
else:
    log_probe(DS, url, f"citations probe failed ({st})", status=st, note=str(d)[:200], probe_id="S2-CONTEXTS")
    print("citations probe:", st, str(d)[:200])

# S2ORC / datasets route: list releases + check dataset listing + key gating
st, d, url = get("https://api.semanticscholar.org/datasets/v1/release/latest", sleep=SLEEP)
if st == 200 and isinstance(d, dict):
    names = [x if isinstance(x, str) else x.get("name") for x in d.get("datasets", [])]
    log_probe(DS, url, f"datasets release={d.get('release_id')} datasets={names}",
              status=st, result={"release_id": d.get("release_id"), "datasets": names}, probe_id="S2ORC-LIST")
    print("\nrelease:", d.get("release_id"), "datasets:", names)
else:
    log_probe(DS, url, f"datasets list failed ({st})", status=st, note=str(d)[:200], probe_id="S2ORC-LIST")
    print("datasets list:", st, str(d)[:200])

# probe the s2orc dataset download endpoint (expect key-gated 403/401 without API key)
st, d, url = get("https://api.semanticscholar.org/datasets/v1/release/latest/dataset/s2orc", sleep=SLEEP)
log_probe(DS, url, f"s2orc dataset download endpoint status={st} (key-gating check)",
          status=st, result={"body": str(d)[:300]}, probe_id="S2ORC-GATE")
print("\ns2orc dataset endpoint (no key):", st, "->", str(d)[:200])

# SPDX-License-Identifier: MIT
"""OpenAlex probe battery (read-only). Generates the linked sample used across sources."""
import json, os
from probe import get, log_probe, MAILTO, RECON_DIR

DS = "openalex"
BASE = "https://api.openalex.org"
POLITE = {"mailto": MAILTO}


def works(params, sleep=1.0):
    p = dict(POLITE); p.update(params)
    return get(f"{BASE}/works", params=p, sleep=sleep)


# A. total works
st, d, url = works({"per-page": 1})
total = d["meta"]["count"] if st == 200 else None
log_probe(DS, url, f"total works = {total:,}" if total else "total FAILED",
          status=st, result={"count": total}, probe_id="OA-A")

# B. is_retracted:true count (verify the filter exists)
st, d, url = works({"filter": "is_retracted:true", "per-page": 1})
retr = d["meta"]["count"] if st == 200 and isinstance(d, dict) and "meta" in d else None
log_probe(DS, url, f"is_retracted:true count = {retr:,}" if retr is not None else f"is_retracted filter FAILED ({st})",
          status=st, result={"count": retr},
          note=None if retr is not None else str(d)[:300], probe_id="OA-B")

# C. is_retracted per publication_year (group_by)
st, d, url = works({"filter": "is_retracted:true", "group_by": "publication_year"})
peryear = None
if st == 200 and isinstance(d, dict) and d.get("group_by"):
    peryear = {g["key"]: g["count"] for g in d["group_by"]}
log_probe(DS, url, f"is_retracted per-year groups = {len(peryear) if peryear else 0}",
          status=st, result={"per_year": peryear}, probe_id="OA-C")

# D. background: ALL works per publication_year (for R3/R4 ratio)
st, d, url = works({"group_by": "publication_year"})
bg_peryear = None
if st == 200 and isinstance(d, dict) and d.get("group_by"):
    bg_peryear = {g["key"]: g["count"] for g in d["group_by"]}
log_probe(DS, url, f"ALL works per-year groups = {len(bg_peryear) if bg_peryear else 0}",
          status=st, result={"per_year": bg_peryear}, probe_id="OA-D")

# E. fetch a real sample of retracted works with join-key fields
sel = "id,doi,ids,title,publication_year,publication_date,referenced_works_count,cited_by_count,is_retracted,primary_topic,abstract_inverted_index"
st, d, url = works({"filter": "is_retracted:true", "per-page": 30, "select": sel}, sleep=1.0)
retr_sample = d.get("results", []) if st == 200 and isinstance(d, dict) else []


def completeness(rows):
    n = len(rows)
    if not n:
        return {}
    def has(f):
        c = 0
        for r in rows:
            v = r.get(f)
            if f == "ids":
                v = r.get("ids", {})
                if v and (v.get("pmid") or v.get("pmcid")):
                    c += 1
            elif f == "referenced_works_count":
                if (r.get("referenced_works_count") or 0) > 0:
                    c += 1
            elif f == "abstract_inverted_index":
                if r.get("abstract_inverted_index"):
                    c += 1
            elif v:
                c += 1
        return c
    return {
        "n": n,
        "has_doi": has("doi"),
        "has_pmid_or_pmcid": has("ids"),
        "has_references": has("referenced_works_count"),
        "has_abstract_ii": has("abstract_inverted_index"),
        "has_topic": has("primary_topic"),
        "has_pubdate": has("publication_date"),
    }


comp = completeness(retr_sample)
log_probe(DS, url, f"retracted sample n={comp.get('n',0)} completeness={comp}",
          status=st, result={"completeness": comp}, probe_id="OA-E")

# F. ordinary (non-retracted) matched sample, same years as retracted sample
years = sorted({r.get("publication_year") for r in retr_sample if r.get("publication_year")})
yr_filter = f"publication_year:{years[len(years)//2]}" if years else "publication_year:2019"
st, d, url = works({"filter": f"is_retracted:false,{yr_filter}", "per-page": 30, "select": sel}, sleep=1.0)
ord_sample = d.get("results", []) if st == 200 and isinstance(d, dict) else []
comp_o = completeness(ord_sample)
log_probe(DS, url, f"ordinary sample ({yr_filter}) n={comp_o.get('n',0)} completeness={comp_o}",
          status=st, result={"completeness": comp_o}, probe_id="OA-F")


def slim(rows, k=12):
    out = []
    for r in rows[:k]:
        ids = r.get("ids", {}) or {}
        out.append({
            "openalex": r.get("id"),
            "doi": (r.get("doi") or "").replace("https://doi.org/", "") or None,
            "pmid": (ids.get("pmid") or "").replace("https://pubmed.ncbi.nlm.nih.gov/", "") or None,
            "pmcid": ids.get("pmcid"),
            "year": r.get("publication_year"),
            "date": r.get("publication_date"),
            "refs": r.get("referenced_works_count"),
            "is_retracted": r.get("is_retracted"),
            "title": (r.get("title") or "")[:120],
        })
    return out


sample = {"retracted": slim(retr_sample), "ordinary": slim(ord_sample)}
with open(os.path.join(RECON_DIR, "sample_records.json"), "w", encoding="utf-8") as f:
    json.dump(sample, f, indent=2, ensure_ascii=False)
log_probe(DS, "local", f"saved sample_records.json: {len(sample['retracted'])} retracted + {len(sample['ordinary'])} ordinary DOIs",
          status="ok", probe_id="OA-G")

print("\n--- retracted per year (last 15) ---")
if peryear:
    for y in sorted((k for k in peryear if str(k).isdigit()), key=int)[-15:]:
        print(f"  {y}: {peryear[y]:,}")
print("\n--- sample retracted DOIs ---")
for r in sample["retracted"]:
    print(f"  {r['doi']}  pmid={r['pmid']}  y={r['year']}  refs={r['refs']}")

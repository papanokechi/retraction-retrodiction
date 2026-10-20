# SPDX-License-Identifier: MIT
"""Crossref + Retraction Watch probe battery (read-only)."""
import json, os
from probe import get, head, log_probe, MAILTO, RECON_DIR

DS = "crossref"
BASE = "https://api.crossref.org"
POLITE = {"mailto": MAILTO}

with open(os.path.join(RECON_DIR, "sample_records.json"), encoding="utf-8") as f:
    sample = json.load(f)

# A. total works in Crossref
st, d, url = get(f"{BASE}/works", params=dict(POLITE, rows=0), sleep=1.0)
total = d.get("message", {}).get("total-results") if st == 200 and isinstance(d, dict) else None
log_probe(DS, url, f"Crossref total works = {total:,}" if total else f"total FAILED ({st})",
          status=st, result={"total": total}, probe_id="CR-A")

# B. retraction-notice count via update-type filter (verify representation)
for filt in ["update-type:retraction", "type:retraction"]:
    st, d, url = get(f"{BASE}/works", params=dict(POLITE, filter=filt, rows=0), sleep=1.0)
    tot = d.get("message", {}).get("total-results") if st == 200 and isinstance(d, dict) else None
    log_probe(DS, url, f"filter '{filt}' -> total = {tot:,}" if tot is not None else f"filter '{filt}' FAILED ({st})",
              status=st, result={"filter": filt, "total": tot}, probe_id=f"CR-B:{filt}")

# C. per-DOI lookups: how is retraction linkage + date represented?
def date_parts(obj, key):
    v = obj.get(key, {})
    if isinstance(v, dict) and v.get("date-parts"):
        return v["date-parts"][0]
    return None

def probe_doi(rec, kind):
    doi = rec.get("doi")
    if not doi:
        return
    st, d, url = get(f"{BASE}/works/{doi}", params=POLITE, sleep=1.0)
    if st != 200 or not isinstance(d, dict):
        log_probe(DS, url, f"[{kind}] {doi} NOT in Crossref ({st})", status=st, probe_id="CR-C")
        return
    m = d["message"]
    rel = m.get("relation", {}) or {}
    upd_to = m.get("update-to", []) or []
    upd_by = m.get("updated-by", []) or []
    info = {
        "doi": doi,
        "type": m.get("type"),
        "issued": date_parts(m, "issued"),
        "created": (m.get("created", {}) or {}).get("date-time"),
        "relation_keys": sorted(rel.keys()),
        "n_update_to": len(upd_to),
        "update_to": [{"type": u.get("type"), "doi": u.get("DOI"),
                        "updated": (u.get("updated", {}) or {}).get("date-parts", [[None]])[0]} for u in upd_to][:3],
        "n_updated_by": len(upd_by),
        "updated_by": [{"type": u.get("type"), "doi": u.get("DOI"),
                        "updated": (u.get("updated", {}) or {}).get("date-parts", [[None]])[0]} for u in upd_by][:3],
    }
    log_probe(DS, url, f"[{kind}] {doi} type={info['type']} rel={info['relation_keys']} upd_to={info['n_update_to']} upd_by={info['n_updated_by']}",
              status=st, result=info, probe_id="CR-C")
    return info

print("--- retracted DOIs in Crossref ---")
resolved = 0
for rec in sample["retracted"]:
    info = probe_doi(rec, "RETR")
    if info:
        resolved += 1
print("--- ordinary DOIs in Crossref (first 5) ---")
for rec in sample["ordinary"][:5]:
    probe_doi(rec, "ORD")

log_probe(DS, "summary", f"retracted DOIs resolving in Crossref: {resolved}/{len(sample['retracted'])}",
          status="ok", probe_id="CR-D")

# E. Retraction Watch bulk route: confirm the CSV exists + size (no full download)
rw_urls = [
    "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv",
    "https://api.labs.crossref.org/data/retractionwatch?rows=0",
]
for u in rw_urls:
    st, hdrs, _ = head(u, sleep=0.5)
    cl = hdrs.get("content-length") or hdrs.get("content-range")
    log_probe("retraction_watch", u, f"RW route probe status={st} size/hdr={cl}",
              status=st, result={"headers": {k: hdrs.get(k) for k in ("content-length","content-range","content-type","content-disposition") if k in hdrs}},
              probe_id="RW-A")
    print(f"  RW {st}: {u} -> {cl}")

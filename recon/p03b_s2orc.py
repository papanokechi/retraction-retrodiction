# SPDX-License-Identifier: MIT
"""S2ORC datasets route + citation-contexts coverage (utf-8 safe, read-only)."""
import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
from probe import get, log_probe, RECON_DIR

DS = "semantic_scholar"
G = "https://api.semanticscholar.org/graph/v1"
D = "https://api.semanticscholar.org/datasets/v1"
SLEEP = 1.3

# datasets release listing (confirms s2orc/s2orc_v2 present + release id)
st, d, url = get(f"{D}/release/latest", sleep=SLEEP)
if st == 200 and isinstance(d, dict):
    names = [x if isinstance(x, str) else x.get("name") for x in d.get("datasets", [])]
    log_probe(DS, url, f"datasets release={d.get('release_id')} datasets={names}",
              status=st, result={"release_id": d.get("release_id"), "datasets": names}, probe_id="S2ORC-LIST")
    print("release:", d.get("release_id"))
    print("datasets:", names)
else:
    log_probe(DS, url, f"datasets list failed ({st})", status=st, note=str(d)[:200], probe_id="S2ORC-LIST")
    print("datasets list:", st, str(d)[:200])

# s2orc download endpoint WITHOUT key -> expect 403/401 (key-gating confirmation)
st, d, url = get(f"{D}/release/latest/dataset/s2orc", sleep=SLEEP)
log_probe(DS, url, f"s2orc dataset endpoint (no key) status={st}",
          status=st, result={"body": str(d)[:300]}, probe_id="S2ORC-GATE")
print("\ns2orc endpoint (no key):", st, "->", str(d)[:160])

# citation contexts coverage on a CS/arXiv paper (full-text parsed -> better context coverage
# than the biomedical sample). Attention Is All You Need = arXiv:1706.03762.
for pid, label in [("ARXIV:1706.03762", "CS/arXiv"), ("DOI:10.1038/nature04533", "biomed-retracted")]:
    st, d, url = get(f"{G}/paper/{pid}/citations",
                     params={"fields": "contexts,intents,isInfluential", "limit": 50}, sleep=SLEEP)
    if st == 200 and isinstance(d, dict):
        data = d.get("data", [])
        with_ctx = sum(1 for c in data if c.get("contexts"))
        with_int = sum(1 for c in data if c.get("intents"))
        infl = sum(1 for c in data if c.get("isInfluential"))
        ex = next((c.get("contexts") for c in data if c.get("contexts")), None)
        log_probe(DS, url, f"[{label}] citations n={len(data)} ctx={with_ctx} intents={with_int} influential={infl}",
                  status=st, result={"label": label, "n": len(data), "with_contexts": with_ctx,
                                     "with_intents": with_int, "influential": infl,
                                     "example_context": (ex or [None])[0]}, probe_id="S2-CONTEXTS2")
        print(f"\n[{label}] n={len(data)} contexts={with_ctx} intents={with_int} influential={infl}")
        if ex:
            print("  example:", str(ex[0])[:180].encode("ascii", "replace").decode())
    else:
        log_probe(DS, url, f"[{label}] citations failed ({st})", status=st, note=str(d)[:150], probe_id="S2-CONTEXTS2")
        print(f"[{label}] citations:", st, str(d)[:120])

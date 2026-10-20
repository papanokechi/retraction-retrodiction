# SPDX-License-Identifier: MIT
"""OpenCitations Index v2 probes (read-only). Citation counts + join fields."""
import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
from probe import get, log_probe, RECON_DIR

DS = "opencitations"
API = "https://api.opencitations.net/index/v2"

with open(os.path.join(RECON_DIR, "sample_records.json"), encoding="utf-8") as f:
    sample = json.load(f)

# pick 2 retracted + 1 ordinary DOI
probes = [(sample["retracted"][0]["doi"], "RETR-1"),
          (sample["retracted"][4]["doi"], "RETR-2"),
          (sample["ordinary"][0]["doi"], "ORD-1")]

for doi, label in probes:
    if not doi:
        continue
    # citation count (incoming)
    st, d, url = get(f"{API}/citation-count/doi:{doi}", sleep=1.5)
    cc = None
    if st == 200 and isinstance(d, list) and d:
        cc = d[0].get("count")
    log_probe(DS, url, f"[{label}] {doi} citation-count={cc}", status=st,
              result={"doi": doi, "citation_count": cc}, probe_id="OC-CCOUNT")
    print(f"[{label}] {doi} -> citation-count={cc}")

# full citations record for one DOI: inspect available join fields
doi0 = sample["retracted"][0]["doi"]
st, d, url = get(f"{API}/citations/doi:{doi0}", sleep=1.5)
if st == 200 and isinstance(d, list):
    fields = sorted(d[0].keys()) if d else []
    ex = d[0] if d else {}
    log_probe(DS, url, f"citations/doi:{doi0} -> n={len(d)} fields={fields}",
              status=st, result={"n": len(d), "fields": fields, "example": ex}, probe_id="OC-CITATIONS")
    print(f"\ncitations/{doi0}: n={len(d)} records")
    print("fields:", fields)
    if ex:
        print("example:", json.dumps(ex, indent=0)[:400])
else:
    log_probe(DS, url, f"citations failed ({st})", status=st, note=str(d)[:200], probe_id="OC-CITATIONS")
    print("citations:", st, str(d)[:200])

# SPDX-License-Identifier: MIT
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
import requests
from probe import log_probe, UA

API = "https://api.opencitations.net/index/v2"
doi = "10.1155/2014/943162"
url = f"{API}/citations/doi:{doi}"
try:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=90)
    d = r.json()
    fields = sorted(d[0].keys()) if d else []
    log_probe("opencitations", url, f"citations/doi:{doi} n={len(d)} fields={fields}",
              status=r.status_code, result={"n": len(d), "fields": fields, "example": d[0] if d else {}},
              probe_id="OC-FIELDS")
    print(f"n={len(d)} fields={fields}")
    print("example:", json.dumps(d[0], indent=0)[:500])
except Exception as e:
    log_probe("opencitations", url, f"requests fetch failed: {type(e).__name__}: {e}", status=None, probe_id="OC-FIELDS")
    print("failed:", type(e).__name__, e)

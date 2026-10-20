# SPDX-License-Identifier: MIT
"""RW bulk-file size + labs API shape (read-only) — urllib-based."""
from probe import get, head, log_probe, MAILTO

RW_CSV = "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"

# size via Range bytes=0-0 -> content-range "bytes 0-0/TOTAL"
st, hdrs, _ = head(RW_CSV, sleep=0.5)
crange = hdrs.get("content-range")
total = crange.split("/")[-1] if crange and "/" in crange else None
# header row via small range read (text)
st2, text, _ = get(RW_CSV, headers={"Range": "bytes=0-2047"}, sleep=1.0, accept="text")
header_line = text.splitlines()[0] if isinstance(text, str) and text else ""
ncols = header_line.count(",") + 1 if header_line else 0
log_probe("retraction_watch", RW_CSV,
          f"RW CSV total_bytes={total} header_cols={ncols}",
          status=st, result={"content_range": crange, "total_bytes": total,
                              "n_header_cols": ncols, "header": header_line[:800]},
          probe_id="RW-SIZE")
print("content-range:", crange, "-> total bytes:", total,
      f"(~{int(total)/1e6:.1f} MB)" if total and total.isdigit() else "")
print("header cols  :", ncols)
print("HEADER:", header_line[:800])

# labs API shape
st, d, url = get("https://api.labs.crossref.org/data/retractionwatch",
                 params={"rows": 1, "mailto": MAILTO}, sleep=1.0)
if isinstance(d, dict):
    msg = d.get("message", {})
    items = msg.get("items", [])
    keys = sorted(items[0].keys()) if items else sorted(msg.keys())
    log_probe("retraction_watch", url, f"labs API total={msg.get('total-results')} item_keys={keys}",
              status=st, result={"total": msg.get("total-results"), "item_keys": keys}, probe_id="RW-LABS")
    print("labs total:", msg.get("total-results"))
    print("labs keys :", keys)
else:
    log_probe("retraction_watch", url, f"labs API non-json ({st})", status=st, probe_id="RW-LABS")
    print("labs API:", st, str(d)[:300])

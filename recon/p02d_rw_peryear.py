# SPDX-License-Identifier: MIT
"""Re-derive Retraction Watch per-year true-Retraction counts from the CACHED CSV
(no re-download) and log as RW-YEAR so the report figures are traceable."""
import sys, csv, os
sys.stdout.reconfigure(encoding="utf-8")
from collections import Counter
from probe import log_probe, RECON_DIR

path = os.path.join(str(RECON_DIR), "retraction_watch.csv")
by_retr, by_orig = Counter(), Counter()
n_ret = 0
with open(path, encoding="utf-8", errors="replace", newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        if (row.get("RetractionNature") or "").strip() != "Retraction":
            continue
        n_ret += 1
        rd = (row.get("RetractionDate") or "").strip()
        od = (row.get("OriginalPaperDate") or "").strip()
        # format MM/DD/YYYY 0:00  -> year is token before first space, last /-part
        def yr(s):
            try:
                return s.split()[0].split("/")[-1]
            except Exception:
                return None
        y1, y2 = yr(rd), yr(od)
        if y1 and y1.isdigit():
            by_retr[y1] += 1
        if y2 and y2.isdigit():
            by_orig[y2] += 1

def series(c):
    return {y: c[y] for y in sorted(c) if 2005 <= int(y) <= 2026}

retr = series(by_retr)
orig = series(by_orig)
print("true Retraction rows:", n_ret)
print("by RetractionDate year:", retr)
print("by OriginalPaperDate year:", orig)
log_probe("retraction_watch", str(path),
          f"true-Retraction={n_ret}; per-year by RetractionDate (2005-2026)",
          status="local_parse", probe_id="RW-YEAR",
          result={"true_retraction": n_ret, "by_retraction_date": retr, "by_original_paper_date": orig})

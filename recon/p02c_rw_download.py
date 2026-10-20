# SPDX-License-Identifier: MIT
"""Download Retraction Watch CSV once (documented bulk route) + analyze for R2/R4/R6."""
import os, io, json, time, urllib.request, datetime
import pandas as pd
from probe import log_probe, UA, RECON_DIR

RW_CSV = "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
LOCAL = os.path.join(RECON_DIR, "retraction_watch.csv")

if not os.path.exists(LOCAL):
    t0 = time.time()
    req = urllib.request.Request(RW_CSV, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r, open(LOCAL, "wb") as f:
        f.write(r.read())
    dt = time.time() - t0
    sz = os.path.getsize(LOCAL)
    log_probe("retraction_watch", RW_CSV,
              f"downloaded RW CSV {sz:,} bytes in {dt:.1f}s (one-time bulk-route confirmation)",
              status=200, result={"bytes": sz, "seconds": round(dt, 1)}, probe_id="RW-DL")
    print(f"downloaded {sz:,} bytes in {dt:.1f}s")
else:
    print("RW CSV already cached")

df = pd.read_csv(LOCAL, dtype=str, keep_default_na=False)
n = len(df)
# RetractionNature distribution
nature = df["RetractionNature"].value_counts().to_dict()
# parse RetractionDate -> year (format like "1/15/2020 0:00" or ISO)
def yr(s):
    s = (s or "").strip()
    for fmt in ("%m/%d/%Y %H:%M", "%m/%d/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.datetime.strptime(s, fmt).year
        except Exception:
            continue
    return None
df["rt_year"] = df["RetractionDate"].map(yr)
true_retr = df[df["RetractionNature"].str.strip().str.lower() == "retraction"]
per_year = (true_retr[true_retr["rt_year"].notna()]
            .groupby("rt_year").size().sort_index())
# join-key completeness
def pct(col):
    nonempty = (df[col].str.strip() != "").sum()
    return round(100 * nonempty / n, 1)
completeness = {c: pct(c) for c in
                ["OriginalPaperDOI", "OriginalPaperPubMedID", "RetractionDOI",
                 "RetractionPubMedID", "RetractionDate", "OriginalPaperDate", "Reason", "Subject"]}

log_probe("retraction_watch", LOCAL,
          f"RW rows={n:,}; nature={nature}; completeness={completeness}",
          status="ok",
          result={"rows": n, "nature": nature, "completeness_pct": completeness,
                  "true_retraction_rows": int(len(true_retr))},
          probe_id="RW-ANALYZE")
print(f"\nRW total rows: {n:,}")
print("RetractionNature:", nature)
print("Join-key completeness %:", json.dumps(completeness, indent=0))
print("\n-- true 'Retraction' rows per year (2010-2024) --")
for y in range(2010, 2025):
    print(f"  {y}: {int(per_year.get(y, 0)):,}")
print(f"  total true-retraction rows: {len(true_retr):,}")

# R2 event-date spot check vs the 12 sample DOIs (compare RW RetractionDate to Crossref)
with open(os.path.join(RECON_DIR, "sample_records.json"), encoding="utf-8") as f:
    sample = json.load(f)
doi_index = {str(d).lower().strip(): i for i, d in enumerate(df["OriginalPaperDOI"])}
print("\n-- R2 spot check: sample retracted DOI -> RW RetractionDate --")
spot = []
for rec in sample["retracted"]:
    doi = (rec.get("doi") or "").lower().strip()
    if doi in doi_index:
        row = df.iloc[doi_index[doi]]
        spot.append({"doi": doi, "rw_retraction_date": row["RetractionDate"],
                     "rw_nature": row["RetractionNature"], "rw_reason": row["Reason"][:60]})
        print(f"  {doi} -> {row['RetractionDate']}  [{row['RetractionNature']}]  {row['Reason'][:50]}")
    else:
        spot.append({"doi": doi, "rw_retraction_date": None})
        print(f"  {doi} -> NOT FOUND in RW")
log_probe("retraction_watch", LOCAL,
          f"R2 spot check: {sum(1 for s in spot if s['rw_retraction_date'])}/{len(spot)} sample DOIs found in RW with dates",
          status="ok", result={"spot": spot}, probe_id="RW-R2SPOT")

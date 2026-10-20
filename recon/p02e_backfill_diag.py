# SPDX-License-Identifier: MIT
"""JC3 backfill diagnostic (read-only, cached CSV — no re-download).
Question: are the 2010-11 RetractionDate-spike records a backfill of genuinely
old retractions (usable for MEMBERSHIP, not for precise timing), or are their
dates themselves unreliable (=> exclude pre-2012 notice dates from timing)?

Method: compare the OriginalPaperDate distribution + notice->paper lag for the
2010-11 notice cohort vs a 'normal' 2018-19 notice cohort. Logged as RW-BACKFILL.
"""
import sys, csv, os, statistics as st
sys.stdout.reconfigure(encoding="utf-8")
from collections import Counter
from probe import log_probe, RECON_DIR

path = os.path.join(str(RECON_DIR), "retraction_watch.csv")

def yr(s):
    try:
        return int((s or "").split()[0].split("/")[-1])
    except Exception:
        return None

def cohort(years):
    orig_years, lags, missing, total = [], [], 0, 0
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("RetractionNature") or "").strip() != "Retraction":
                continue
            ry = yr(row.get("RetractionDate"))
            if ry not in years:
                continue
            total += 1
            oy = yr(row.get("OriginalPaperDate"))
            if oy is None or oy < 1900 or oy > ry:
                missing += 1
                continue
            orig_years.append(oy)
            lags.append(ry - oy)
    return total, orig_years, lags, missing

def summarize(label, years):
    total, oy, lags, missing = cohort(years)
    spread = Counter()
    for y in oy:
        spread[(y // 5) * 5] += 1  # 5-year bins
    long_lag = sum(1 for l in lags if l > 10)
    res = {
        "notice_years": sorted(years),
        "total_records": total,
        "orig_date_missing_or_invalid": missing,
        "missing_pct": round(100 * missing / total, 1) if total else None,
        "orig_year_min": min(oy) if oy else None,
        "orig_year_median": int(st.median(oy)) if oy else None,
        "orig_year_max": max(oy) if oy else None,
        "lag_median_yrs": st.median(lags) if lags else None,
        "lag_p90_yrs": (sorted(lags)[int(0.9 * len(lags))] if lags else None),
        "lag_gt_10yr_pct": round(100 * long_lag / len(lags), 1) if lags else None,
        "orig_year_5yr_bins": dict(sorted(spread.items())),
    }
    print(f"\n=== {label} (notice {sorted(years)}) ===")
    for k, v in res.items():
        if k != "orig_year_5yr_bins":
            print(f"  {k}: {v}")
    print("  orig_year_5yr_bins:", res["orig_year_5yr_bins"])
    return res

backfill = summarize("BACKFILL cohort", {2010, 2011})
normal = summarize("NORMAL cohort", {2018, 2019})

verdict = (
    "usable-for-membership" if (backfill["missing_pct"] is not None
        and backfill["missing_pct"] < 15 and (backfill["lag_median_yrs"] or 0) >= 2)
    else "dates-unreliable-exclude-pre2012-timing"
)
print("\nVERDICT:", verdict)
log_probe("retraction_watch", path,
          f"2010-11 backfill diagnostic: verdict={verdict}",
          status="local_parse", probe_id="RW-BACKFILL",
          result={"backfill_2010_11": backfill, "normal_2018_19": normal, "verdict": verdict})

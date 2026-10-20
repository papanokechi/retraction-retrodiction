# SPDX-License-Identifier: MIT
"""Gate 3 — snapshot pinning for the retraction-retrodiction lock.

On LOCK DAY this records the exact, reproducible snapshot identity of every
pinned source into ``charter/snapshot_pins.yaml`` — the frozen substrate the
pre-registration and the Zenodo redeposit are defined against (charter JC4/§2).

Sources pinned (all sanctioned CC0 / ODC-BY bulk routes, R1):
  * OpenAlex        — snapshot release id from s3://openalex RELEASE_NOTES.txt
  * Retraction Watch— fresh CSV from Crossref's GitLab mirror: date+rows+SHA-256
  * Crossref        — annual public-data-file year + coverage + torrent DOI
  * PMC OA subset   — oa_file_list.csv Last-Modified (continuous corpus)
  * OpenCitations   — latest Index dump release

Two modes:
  --dry-run  (default) probe every lookup live, print a DRY_RUN table, write
             NOTHING. Used now to prove the lookups work without pinning.
  --pin      the real lock-day run: fetch fresh (incl. the full RW CSV) and
             write charter/snapshot_pins.yaml. Only run on the operator's word.

This helper reads only public CC0/ODC-BY artifacts, so it is intentionally NOT
behind the harvest contact-guard (recon/probe.py) — that guard protects the
polite-pool harvest, not static-artifact pinning. It still sends a descriptive
User-Agent (with the configured contact email if one is available).

stdlib only. Usage:
    python scripts/pin_snapshots.py            # dry-run
    python scripts/pin_snapshots.py --pin      # lock-day pin (writes yaml)
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import io
import csv
import os
import re
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def _today() -> str:
    return datetime.date.today().isoformat()


def _repo_root() -> str:
    d = SCRIPT_DIR
    for _ in range(6):
        if os.path.isdir(os.path.join(d, "charter")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.dirname(SCRIPT_DIR)  # assume scripts/ sits under the root


def _contact() -> str:
    """Best-effort contact email for the pin User-Agent (env or config)."""
    env = (os.environ.get("RRP_CONTACT_EMAIL") or "").strip()
    if env:
        return env
    d = SCRIPT_DIR
    for _ in range(6):
        cand = os.path.join(d, "config", "contact.yaml")
        if os.path.exists(cand):
            try:
                with open(cand, encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if s.startswith("contact_email:"):
                            v = s.split(":", 1)[1].split(" #", 1)[0].strip().strip("\"'")
                            return v if "@" in v and "example" not in v.lower() else ""
            except Exception:
                return ""
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return ""


def _ua() -> str:
    e = _contact()
    tail = f"mailto:{e}" if "@" in e else "public CC0 snapshot pinning"
    return f"retraction-retrodiction-pin/0.1 (+{tail})"


def _errstr(x) -> str:
    if isinstance(x, (bytes, bytearray)):
        return x[:200].decode("utf-8", "replace")
    return str(x)[:200]


def _get(url, timeout=90):
    """Full GET. Returns (status, bytes, headers) or (None, err, {})."""
    req = urllib.request.Request(url, headers={"User-Agent": _ua()})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        data = r.read()
        return r.getcode(), data, {k.lower(): v for k, v in r.getheaders()}
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        return e.code, body, {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
    except Exception as e:
        return None, f"ERROR: {type(e).__name__}: {e}", {}


def _head(url, timeout=60):
    """True HEAD (no body). Returns (status, headers)."""
    req = urllib.request.Request(url, headers={"User-Agent": _ua()}, method="HEAD")
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.getcode(), {k.lower(): v for k, v in r.getheaders()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {e}"}


def _peek(url, nbytes=4096, timeout=90):
    """Read at most nbytes then abort — safe size probe for large files.
    Returns (status, headers, first_bytes). Even if the server ignores Range
    and returns 200, we read only nbytes and close, so no full download."""
    req = urllib.request.Request(
        url, headers={"User-Agent": _ua(), "Range": f"bytes=0-{nbytes - 1}"})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        hdr = {k.lower(): v for k, v in r.getheaders()}
        chunk = r.read(nbytes)
        r.close()
        return r.getcode(), hdr, chunk
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}, b""
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {e}"}, b""


# --- per-source pin probes -------------------------------------------------

OPENALEX_RELEASE_NOTES = "https://openalex.s3.amazonaws.com/RELEASE_NOTES.txt"
RW_CSV = "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
CROSSREF_PDF = "https://www.crossref.org/services/metadata-retrieval/public-data-file/"
PMC_OA_FILELIST = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz"
OPENCITATIONS_DL = "https://download.opencitations.net"


def pin_openalex() -> dict:
    e = {"source": "OpenAlex", "layer": "backbone / background / target flag",
         "route": "s3://openalex (RELEASE_NOTES.txt)", "bucket": "s3://openalex/data",
         "license": "CC0", "source_url": OPENALEX_RELEASE_NOTES, "retrieved_at": _now()}
    st, data, _ = _get(OPENALEX_RELEASE_NOTES)
    e["status"] = st
    if st == 200 and isinstance(data, (bytes, bytearray)):
        text = data.decode("utf-8", "replace")
        m = re.search(r"RELEASE\s+(\d{4}-\d{2}-\d{2})", text)
        e["snapshot_release_id"] = m.group(1) if m else None
        e["release_notes_sha256"] = hashlib.sha256(data).hexdigest()
    else:
        e["error"] = _errstr(data)
    return e


def pin_retraction_watch(full: bool) -> dict:
    e = {"source": "Retraction Watch (via Crossref)", "layer": "event layer (primary)",
         "route": "GitLab crossref/retraction-watch-data raw CSV, daily",
         "license": "CC0", "source_url": RW_CSV, "retrieved_at": _now()}
    if full:
        st, data, _ = _get(RW_CSV, timeout=300)
        e["status"] = st
        if st in (200, 206) and isinstance(data, (bytes, bytearray)):
            e["bytes"] = len(data)
            e["sha256"] = hashlib.sha256(data).hexdigest()
            try:
                rows = sum(1 for _ in csv.reader(
                    io.StringIO(data.decode("utf-8", "replace")))) - 1
                e["row_count"] = rows
            except Exception as ex:
                e["row_count_error"] = str(ex)[:120]
            e["csv_date"] = _today()
        else:
            e["error"] = _errstr(data)
    else:
        st, hdr, chunk = _peek(RW_CSV)
        e["status"] = st
        cr = hdr.get("content-range")
        e["reported_total_bytes"] = (cr.split("/")[-1] if cr and "/" in cr
                                     else hdr.get("content-length"))
        try:
            e["header_cols"] = (chunk.decode("utf-8", "replace").splitlines()[0].count(",") + 1
                                if chunk else None)
        except Exception:
            e["header_cols"] = None
        e["note"] = ("DRY_RUN: HEAD/peek only; the --pin run downloads the fresh "
                     "CSV and records csv_date + row_count + sha256")
        if not (st and st < 400):
            e["error"] = hdr.get("error") or f"HTTP {st}"
    return e


def pin_crossref() -> dict:
    e = {"source": "Crossref public data file", "layer": "typed events / references / sensitivity",
         "route": "Academic Torrents (annual) + AWS requester-pays",
         "license": "metadata CC0; abstracts copyright",
         "source_url": CROSSREF_PDF, "retrieved_at": _now()}
    st, data, _ = _get(CROSSREF_PDF)
    e["status"] = st
    if st == 200 and isinstance(data, (bytes, bytearray)):
        text = data.decode("utf-8", "replace")
        my = re.search(r"(\d{4})\s+Public data file", text)
        e["public_data_file_year"] = my.group(1) if my else None
        mmil = re.search(r"([\d.]+)\s+million records", text)
        e["record_count"] = (mmil.group(0) if mmil else None)
        mthru = re.search(r"registered up to and including[^.\"<]+", text)
        e["coverage"] = (mthru.group(0).strip() if mthru else None)
        mdoi = re.search(r"10\.13003/[A-Za-z0-9\-]+", text)
        e["torrent_doi"] = ("https://doi.org/" + mdoi.group(0)) if mdoi else None
        e["note"] = ("confirm the torrent DOI / download link on the page's "
                     "'Release notes' + 'Public data file' links at pin time")
    else:
        e["error"] = _errstr(data)
    return e


def pin_pmc() -> dict:
    e = {"source": "PMC OA subset", "layer": "full-text (secondary, biomedical)",
         "route": "s3://pmc-oa-opendata full text (+ FTP PMC-ids.csv.gz join keys)",
         "bucket": "s3://pmc-oa-opendata",
         "license": "per-article Creative Commons (mixed license_code)",
         "source_url": PMC_OA_FILELIST, "retrieved_at": _now()}
    st, hdr = _head(PMC_OA_FILELIST)
    e["status"] = st
    if st and st < 400:
        e["pmc_ids_last_modified"] = hdr.get("last-modified")
        e["pmc_ids_bytes"] = hdr.get("content-length")
        e["snapshot_date_basis"] = ("PMC OA full text is continuous; pin = access "
                                    "date + PMC-ids.csv.gz Last-Modified (the "
                                    "PMID/PMCID/DOI join table, updated daily). "
                                    "Legacy oa.fcgi + FTP OA lists removed Aug 2026 "
                                    "-> full text via s3://pmc-oa-opendata by PMCID.version")
    else:
        e["error"] = hdr.get("error") or f"HTTP {st}"
        e["note"] = "if HEAD blocked, pin as access-date against s3://pmc-oa-opendata baseline"
    return e


def pin_opencitations() -> dict:
    e = {"source": "OpenCitations Index", "layer": "citation links (cross-check)",
         "route": "download.opencitations.net (Figshare-hosted dumps)",
         "license": "CC0", "source_url": OPENCITATIONS_DL, "retrieved_at": _now()}
    st, data, _ = _get(OPENCITATIONS_DL)
    e["status"] = st
    if st == 200 and isinstance(data, (bytes, bytearray)):
        text = data.decode("utf-8", "replace")
        m = (re.search(r"Latest[:\s]+([A-Z][a-z]+\s+\d{4})\s+dump", text)
             or re.search(r"([A-Z][a-z]+\s+\d{4})\s+dump", text))
        e["latest_index_dump"] = m.group(1) if m else None
        if not m:
            e["note"] = "confirm latest Index dump label on the download page at pin time"
    else:
        e["error"] = _errstr(data)
    return e


# --- yaml emission (hand-rolled; values are simple scalars) -----------------

_YAML_IMPLICIT = re.compile(
    r"^("
    r"\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}.*)?"   # date / datetime
    r"|[-+]?\d+(\.\d+)?"                        # int / float
    r"|0x[0-9a-fA-F]+|0o[0-7]+"                 # hex / octal
    r"|true|false|yes|no|on|off|null|~"         # bool / null
    r")$", re.IGNORECASE)


def _yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    # Quote if empty, whitespace-padded, contains YAML-significant chars, or
    # would be implicitly re-typed (a date/number/bool string must stay a string).
    if (s == "" or re.search(r"[:#\"']", s) or s != s.strip()
            or _YAML_IMPLICIT.match(s)):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _emit_yaml(doc: dict) -> str:
    lines = ["# snapshot_pins.yaml — generated by scripts/pin_snapshots.py",
             "# The frozen reproducibility substrate for the Design-A lock (charter §2).",
             "# DO NOT hand-edit; re-run scripts/pin_snapshots.py --pin to regenerate.",
             ""]
    for k, v in doc.items():
        if isinstance(v, dict):
            lines.append(f"{k}:")
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    lines.append(f"  {kk}:")
                    for k3, v3 in vv.items():
                        lines.append(f"    {k3}: {_yaml_scalar(v3)}")
                else:
                    lines.append(f"  {kk}: {_yaml_scalar(vv)}")
        else:
            lines.append(f"{k}: {_yaml_scalar(v)}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pin snapshot identities for the lock.")
    ap.add_argument("--pin", action="store_true",
                    help="REAL lock-day pin: fetch fresh (incl. full RW CSV) and "
                         "write charter/snapshot_pins.yaml")
    ap.add_argument("--dry-run", action="store_true",
                    help="probe lookups, print, write nothing (default)")
    args = ap.parse_args(argv)
    real = args.pin and not args.dry_run
    mode = "PIN" if real else "DRY_RUN"

    print(f"=== pin_snapshots.py [{mode}] {_now()} ===")
    if not real:
        print("(dry-run: proving the lookups resolve; NOTHING is pinned)\n")

    sources = {
        "openalex": pin_openalex(),
        "retraction_watch": pin_retraction_watch(full=real),
        "crossref": pin_crossref(),
        "pmc_oa": pin_pmc(),
        "opencitations": pin_opencitations(),
    }

    key_field = {
        "openalex": "snapshot_release_id",
        "retraction_watch": "sha256" if real else "reported_total_bytes",
        "crossref": "public_data_file_year",
        "pmc_oa": "pmc_ids_last_modified",
        "opencitations": "latest_index_dump",
    }
    errors = 0
    for name, e in sources.items():
        ok = "error" not in e
        errors += 0 if ok else 1
        headline = e.get(key_field[name])
        flag = "OK " if ok else "ERR"
        print(f"[{flag}] {name:<16} status={str(e.get('status')):<5} "
              f"{key_field[name]}={headline}")
        if not ok:
            print(f"        -> {e['error']}")

    doc = {"pin_mode": mode, "generated_at": _now(),
           "charter_ref": "design_A_charter_DRAFT.md §2", "sources": sources}

    print()
    if real:
        out = os.path.join(_repo_root(), "charter", "snapshot_pins.yaml")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(_emit_yaml(doc))
        print(f"PINNED -> {out}")
        print("Next (LOCK_PROCEDURE.md): commit snapshot_pins.yaml, flip the "
              "charter status to LOCKED, tag charter-lock-v1.")
    else:
        print("DRY_RUN complete — no file written. On lock day, after Gate 1 "
              "(contact.yaml) is set, run:  python scripts/pin_snapshots.py --pin")
    if errors:
        print(f"\n{errors} source(s) errored — investigate before a real pin.")
    return 1 if (errors and real) else 0


if __name__ == "__main__":
    sys.exit(main())

# SPDX-License-Identifier: MIT
"""Read-only probe harness for the retraction-retrodiction program.

Every network probe is appended to probe_log.jsonl with a UTC+local timestamp.
Polite by default: descriptive User-Agent, mailto in polite-pool params (caller
supplies), and a sleep after every request. NO scraping of HTML pages — JSON/CSV
API endpoints and documented bulk routes only.

CONTACT IDENTITY (Gate 1). The polite-pool email is no longer hardcoded. It is
read from config/contact.yaml (key `contact_email`) or the RRP_CONTACT_EMAIL
environment variable. A startup guard (`require_contact`) refuses every network
call until that value is a real, email-shaped address that is NOT a reserved
placeholder — so no harvest can go out under the recon placeholder.
"""
from __future__ import annotations
import json, os, re, time, datetime
import urllib.request, urllib.parse, urllib.error

RECON_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(RECON_DIR, "probe_log.jsonl")

# --- contact configuration + network guard (Gate 1a / 1c) ------------------

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# RFC 2606 names reserved for documentation must never reach a live service.
_RESERVED_DOMAINS = {"example.com", "example.org", "example.net"}
_RESERVED_TLDS = (".example", ".test", ".invalid", ".localhost")
# Known placeholders shipped in templates / used during recon.
_PLACEHOLDER_EMAILS = {"recon@example.org"}
_PLACEHOLDER_TOKENS = ("replace_with", "your_real_email", "your_email",
                       "youremail", "changeme", "placeholder")


def is_valid_contact(email) -> bool:
    """True only for a real, email-shaped address that is not a reserved
    placeholder. Unit-tested directly and used by the network guard."""
    if not email or not isinstance(email, str):
        return False
    e = email.strip().lower()
    if not _EMAIL_RE.match(e):
        return False
    if e in _PLACEHOLDER_EMAILS:
        return False
    domain = e.rsplit("@", 1)[-1]
    if domain in _RESERVED_DOMAINS or domain.endswith(_RESERVED_TLDS):
        return False
    if any(tok in e for tok in _PLACEHOLDER_TOKENS):
        return False
    return True


def _find_config_file(name: str = "contact.yaml"):
    """Walk up from this file looking for config/<name>. Works whether the
    harness sits in recon/ (repo layout) or flat (recon workspace)."""
    d = RECON_DIR
    for _ in range(6):
        cand = os.path.join(d, "config", name)
        if os.path.exists(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def _parse_flat_yaml(text: str) -> dict:
    """Minimal stdlib parser for the flat `key: value` contact file (no
    nesting, no lists). Keeps the core harness free of a PyYAML dependency."""
    cfg = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        key, _, val = s.partition(":")
        val = val.split(" #", 1)[0].strip()  # drop trailing inline comment
        if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
            val = val[1:-1]
        cfg[key.strip()] = val
    return cfg


def load_contact() -> dict:
    """Return the contact config dict from config/contact.yaml (or {})."""
    path = _find_config_file()
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return _parse_flat_yaml(f.read())
    except Exception:
        return {}


def contact_email() -> str:
    """Resolved contact email: RRP_CONTACT_EMAIL env wins, else the config."""
    env = os.environ.get("RRP_CONTACT_EMAIL")
    if env and env.strip():
        return env.strip()
    return (load_contact().get("contact_email") or "").strip()


def require_contact() -> str:
    """Guard: return the contact email, or raise RuntimeError if it is missing,
    a placeholder, or not email-shaped. Called before every network request so
    no call can go out under a placeholder identity. This is a *configuration*
    error, deliberately distinct from the network/HTTP errors get()/head()
    swallow."""
    email = contact_email()
    if not is_valid_contact(email):
        raise RuntimeError(
            "Refusing network call: contact email is missing, still a "
            f"placeholder, or not email-shaped (resolved: {email!r}). Set "
            "`contact_email` in config/contact.yaml (or the RRP_CONTACT_EMAIL "
            "env var) to a real address. See WALKTHROUGH.md Gate 1."
        )
    return email


def ncbi_tool() -> str:
    return (os.environ.get("RRP_NCBI_TOOL")
            or load_contact().get("ncbi_tool") or "retraction-retrodiction").strip()


def ncbi_api_key() -> str:
    return (os.environ.get("RRP_NCBI_API_KEY")
            or load_contact().get("ncbi_api_key") or "").strip()


def _ua(email: str) -> str:
    return f"retraction-retrodiction/0.1 (research; mailto:{email})"


# Import-time convenience snapshots. The live guard (require_contact, invoked
# inside get()/head()) is the real enforcement; these just spare callers a
# lookup. CONTACT_EMAIL/MAILTO may hold a placeholder here — that is fine,
# because any network call re-resolves and validates before it goes out.
CONTACT_EMAIL = contact_email()
MAILTO = CONTACT_EMAIL  # back-compat alias for existing probes
NCBI_TOOL = ncbi_tool()
UA = (_ua(CONTACT_EMAIL) if is_valid_contact(CONTACT_EMAIL)
      else "retraction-retrodiction/0.1 (research; contact-not-configured)")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def log_probe(dataset, endpoint, summary, status=None, params=None,
              result=None, note=None, probe_id=None):
    rec = {
        "ts": _now(),
        "probe_id": probe_id,
        "dataset": dataset,
        "endpoint": endpoint,
        "params": params,
        "status": status,
        "summary": summary,
        "result": result,
        "note": note,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tag = f"[{status}]" if status is not None else "[---]"
    print(f"{tag} {dataset}: {summary}")
    return rec


def get(url, params=None, headers=None, sleep=1.0, timeout=60, accept="json"):
    """GET a URL. Returns (status, parsed_or_text, final_url). Never raises for
    network/HTTP conditions — but WILL raise RuntimeError if the contact guard
    fails (a configuration error, not a network one)."""
    email = require_contact()
    if params:
        sep = "&" if "?" in url else "?"
        url = url + sep + urllib.parse.urlencode(params)
    h = {"User-Agent": _ua(email)}
    if accept == "json":
        h["Accept"] = "application/json"
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        raw = r.read()
        status = r.getcode()
        time.sleep(sleep)
        text = raw.decode("utf-8", "replace")
        if accept == "json":
            try:
                return status, json.loads(text), url
            except Exception:
                return status, text, url
        return status, text, url
    except urllib.error.HTTPError as e:
        time.sleep(sleep)
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body[:800], url
    except Exception as e:
        time.sleep(sleep)
        return None, f"ERROR: {type(e).__name__}: {e}", url


def head(url, sleep=0.5, timeout=45):
    """HEAD-like probe via GET Range: bytes=0-0 to confirm a bulk file exists
    without downloading it. Returns (status, headers_dict, final_url). Raises
    RuntimeError if the contact guard fails (configuration error)."""
    email = require_contact()
    h = {"User-Agent": _ua(email), "Range": "bytes=0-0"}
    req = urllib.request.Request(url, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        hdrs = {k.lower(): v for k, v in r.getheaders()}
        status = r.getcode()
        time.sleep(sleep)
        return status, hdrs, url
    except urllib.error.HTTPError as e:
        time.sleep(sleep)
        hdrs = {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
        return e.code, hdrs, url
    except Exception as e:
        time.sleep(sleep)
        return None, {"error": f"{type(e).__name__}: {e}"}, url

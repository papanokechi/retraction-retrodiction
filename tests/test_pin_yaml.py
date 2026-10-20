# SPDX-License-Identifier: MIT
"""Hermetic tests for the snapshot-pins YAML writer (scripts/pin_snapshots.py).

No network. Exercises the lock-day serialization path so a real `--pin` run is
known-good before it is trusted on lock day. If PyYAML is present the output is
parsed back and values are round-tripped; otherwise structural checks apply.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _cand in (os.path.join(os.path.dirname(_HERE), "scripts"), os.path.dirname(_HERE)):
    if os.path.exists(os.path.join(_cand, "pin_snapshots.py")):
        sys.path.insert(0, _cand)
        break
import pin_snapshots as pin  # noqa: E402

SAMPLE = {
    "pin_mode": "PIN",
    "generated_at": "2026-08-01T09:00:00+09:00",
    "charter_ref": "design_A_charter_DRAFT.md §2",
    "sources": {
        "openalex": {
            "source": "OpenAlex",
            "snapshot_release_id": "2026-06-25",
            "release_notes_sha256": "a" * 64,
            "source_url": "https://openalex.s3.amazonaws.com/RELEASE_NOTES.txt",
            "status": 200,
        },
        "retraction_watch": {
            "source": "Retraction Watch (via Crossref)",
            "row_count": 71027,
            "sha256": "b" * 64,
            "csv_date": "2026-08-01",
        },
    },
}


def test_yaml_scalar_quotes_risky_values():
    assert pin._yaml_scalar("https://x.org/a:b").startswith('"')
    assert pin._yaml_scalar("") == '""'
    assert pin._yaml_scalar(200) == "200"
    assert pin._yaml_scalar(None) == "null"
    # date-like strings must be quoted so they never re-type to date objects
    assert pin._yaml_scalar("2026-06-25") == '"2026-06-25"'
    assert pin._yaml_scalar("January 2026") == "January 2026"  # plain, unquoted


def test_emit_yaml_structure():
    text = pin._emit_yaml(SAMPLE)
    assert "pin_mode: PIN" in text
    assert "sources:" in text
    assert "  openalex:" in text
    assert '    snapshot_release_id: "2026-06-25"' in text
    # a URL (has colons) must be quoted
    assert '"https://openalex.s3.amazonaws.com/RELEASE_NOTES.txt"' in text


def test_emit_yaml_roundtrips_if_pyyaml():
    text = pin._emit_yaml(SAMPLE)
    try:
        import yaml
    except Exception:
        return  # PyYAML optional; structural test above still ran
    loaded = yaml.safe_load(text)
    assert loaded["pin_mode"] == "PIN"
    assert loaded["sources"]["openalex"]["snapshot_release_id"] == "2026-06-25"
    assert loaded["sources"]["retraction_watch"]["row_count"] == 71027


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(tests)}/{len(tests)} pin-yaml tests passed")

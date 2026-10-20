# SPDX-License-Identifier: MIT
"""Unit tests for the Gate 1 contact-email guard (recon/probe.py).

Hermetic — no real network. Proves the guard FIRES on placeholder / malformed
contact emails (refusing the network call before it is made) and PASSES a real,
email-shaped value. Runs under pytest, or standalone:

    python tests/test_contact_guard.py
"""
import os
import sys

# Make the probe harness importable whether it sits in ../recon (repo layout)
# or one level up (recon workspace).
_HERE = os.path.dirname(os.path.abspath(__file__))
for _cand in (os.path.join(os.path.dirname(_HERE), "recon"), os.path.dirname(_HERE)):
    if os.path.exists(os.path.join(_cand, "probe.py")):
        sys.path.insert(0, _cand)
        break
import probe  # noqa: E402

REAL = "jane.doe@sheffield.ac.uk"
PLACEHOLDER = "recon@example.org"
TEMPLATE = "REPLACE_WITH_YOUR_REAL_EMAIL@example.com"


def _set_env(email):
    if email is None:
        os.environ.pop("RRP_CONTACT_EMAIL", None)
    else:
        os.environ["RRP_CONTACT_EMAIL"] = email


def test_is_valid_contact_accepts_real():
    assert probe.is_valid_contact(REAL)
    assert probe.is_valid_contact("a.b-c@dept.univ.ac.uk")


def test_is_valid_contact_rejects_placeholders_and_malformed():
    for bad in (None, "", "   ", "not-an-email", "no@tld",
                PLACEHOLDER, TEMPLATE,
                "someone@example.com", "x@example.org", "y@host.invalid",
                "z@service.test", "w@my.localhost"):
        assert not probe.is_valid_contact(bad), bad


def test_require_contact_raises_on_placeholder_passes_on_real():
    old = os.environ.get("RRP_CONTACT_EMAIL")
    try:
        _set_env(PLACEHOLDER)
        try:
            probe.require_contact()
            raised = False
        except RuntimeError:
            raised = True
        assert raised, "guard did not fire on the placeholder"

        _set_env(REAL)
        assert probe.require_contact() == REAL
    finally:
        _set_env(old)


def test_get_refuses_network_on_placeholder_but_proceeds_on_real():
    """get() must raise the guard BEFORE touching the network under a
    placeholder, and reach urlopen once the contact email is real."""
    old = os.environ.get("RRP_CONTACT_EMAIL")
    calls = {"n": 0}

    def fake_urlopen(*a, **k):
        calls["n"] += 1
        raise OSError("network blocked in test")

    real_urlopen = probe.urllib.request.urlopen
    probe.urllib.request.urlopen = fake_urlopen
    try:
        # placeholder -> RuntimeError, network never touched
        _set_env(PLACEHOLDER)
        try:
            probe.get("https://example.invalid/should-not-be-called", sleep=0)
            guard_fired = False
        except RuntimeError:
            guard_fired = True
        assert guard_fired, "get() did not refuse a placeholder contact"
        assert calls["n"] == 0, "network was touched despite placeholder guard"

        # real -> guard passes, get() proceeds to urlopen (which we stubbed)
        _set_env(REAL)
        result = probe.get("https://api.openalex.org/works?per-page=1", sleep=0)
        assert calls["n"] == 1, "get() did not reach the network with a real email"
        assert isinstance(result, tuple) and len(result) == 3
    finally:
        probe.urllib.request.urlopen = real_urlopen
        _set_env(old)


def test_head_also_guarded():
    old = os.environ.get("RRP_CONTACT_EMAIL")
    try:
        _set_env(PLACEHOLDER)
        try:
            probe.head("https://example.invalid/x", sleep=0)
            raised = False
        except RuntimeError:
            raised = True
        assert raised, "head() did not refuse a placeholder contact"
    finally:
        _set_env(old)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(tests)}/{len(tests)} contact-guard tests passed")

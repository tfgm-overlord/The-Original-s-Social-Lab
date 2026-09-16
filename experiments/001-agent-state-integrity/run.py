"""Minimal deterministic harness for Experiment 001.

This is a mechanism-level smoke test, not evidence of LLM efficacy. It makes the
state transition and dependency rules executable before a model is introduced.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent


def load_scenario():
    return json.loads((ROOT / "scenario.json").read_text(encoding="utf-8"))


def superseded_ids(events):
    result = set()
    for event in events:
        result.update(event.get("supersedes", []))
    return result


def baseline(events):
    """Flat-history baseline: retain every claim as usable history."""
    database_claims = [e for e in events if "database" in e["claim"].lower()]
    latest_database = database_claims[-1]["claim"]
    derived_claims = [e for e in events if e.get("derived_from")]
    return {
        "database_claim": latest_database,
        "usable_derived_claims": [e["id"] for e in derived_claims],
        "action": "use the latest database claim and all retained derived claims",
    }


def state_aware(events):
    """Apply supersession to dependency status without deleting history."""
    superseded = superseded_ids(events)
    status = {}

    for event in events:
        status[event["id"]] = "current"

    for event in events:
        parents = event.get("derived_from", [])
        if any(parent in superseded for parent in parents):
            status[event["id"]] = "needs_revalidation"

    current_database = next(
        e["claim"]
        for e in reversed(events)
        if "database" in e["claim"].lower() and e["id"] not in superseded
    )

    usable = [
        event["id"]
        for event in events
        if event.get("derived_from") and status[event["id"]] == "current"
    ]

    return {
        "database_claim": current_database,
        "usable_derived_claims": usable,
        "needs_revalidation": [
            event["id"] for event in events if status[event["id"]] == "needs_revalidation"
        ],
        "action": "use current state; revalidate derived claims whose support depends on superseded state",
    }


def main():
    scenario = load_scenario()
    events = scenario["events"]
    result = {
        "experiment": "001-agent-state-integrity",
        "status": "mechanism_smoke_test",
        "baseline": baseline(events),
        "state_aware": state_aware(events),
        "expected": scenario["expected"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

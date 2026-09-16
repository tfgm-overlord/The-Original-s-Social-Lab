"""Deterministic mechanism harness for Experiment 001.

This is a mechanism-level test, not evidence of LLM efficacy. It checks whether
explicit supersession and dependency metadata produce the expected state view.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent


def load_scenario(path: Path = ROOT / "scenario.json") -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def index_events(events: list[dict]) -> dict[str, dict]:
    ids = [event.get("id") for event in events]
    if any(not event_id for event_id in ids):
        raise ValueError("every event requires a non-empty id")
    if len(ids) != len(set(ids)):
        raise ValueError("event ids must be unique")
    return {event["id"]: event for event in events}


def validate(events: list[dict]) -> dict[str, dict]:
    by_id = index_events(events)
    for event in events:
        if event.get("kind") not in {"state", "derived", "evidence"}:
            raise ValueError(f"{event['id']} has invalid kind")
        if not isinstance(event.get("state_version"), int) or event["state_version"] < 1:
            raise ValueError(f"{event['id']} has invalid state_version")
        if event["kind"] == "state" and not event.get("subject"):
            raise ValueError(f"{event['id']} state event requires a subject")
        for field in ("supersedes", "derived_from", "independent_support"):
            for reference in event.get(field, []):
                if reference not in by_id:
                    raise ValueError(
                        f"{event['id']} references unknown event {reference} via {field}"
                    )
    return by_id


def superseded_ids(events: list[dict]) -> set[str]:
    result: set[str] = set()
    for event in events:
        result.update(event.get("supersedes", []))
    return result


def baseline(events: list[dict]) -> dict:
    """Naive baseline: latest-in-history state and all retained derived claims."""
    current_by_subject: dict[str, str] = {}
    for event in events:
        if event["kind"] == "state":
            current_by_subject[event["subject"]] = event["id"]
    return {
        "current_by_subject": current_by_subject,
        "usable_derived_claims": [
            event["id"] for event in events if event["kind"] == "derived"
        ],
        "action": "use retained derived claims without dependency revalidation",
    }


def dependency_status(events: list[dict]) -> dict[str, str]:
    """Classify derived claims without deleting their historical provenance."""
    by_id = validate(events)
    superseded = superseded_ids(events)
    memo: dict[str, bool] = {}

    def has_superseded_ancestor(event_id: str, trail: tuple[str, ...] = ()) -> bool:
        if event_id in memo:
            return memo[event_id]
        if event_id in trail:
            cycle = " -> ".join(trail + (event_id,))
            raise ValueError(f"derived dependency cycle detected: {cycle}")
        if event_id in superseded:
            memo[event_id] = True
            return True
        event = by_id[event_id]
        result = any(
            has_superseded_ancestor(parent, trail + (event_id,))
            for parent in event.get("derived_from", [])
        )
        memo[event_id] = result
        return result

    status = {event["id"]: "current" for event in events}
    for event in events:
        event_id = event["id"]
        if event_id in superseded:
            status[event_id] = "superseded"
            continue
        if event["kind"] != "derived" or not has_superseded_ancestor(event_id):
            continue
        independent = event.get("independent_support", [])
        if independent and all(not has_superseded_ancestor(ref) for ref in independent):
            status[event_id] = "current"
        else:
            status[event_id] = "needs_revalidation"
    return status


def state_aware(events: list[dict]) -> dict:
    by_id = validate(events)
    status = dependency_status(events)
    current_by_subject: dict[str, str] = {}
    for event in events:
        if event["kind"] != "state" or status[event["id"]] != "current":
            continue
        current = current_by_subject.get(event["subject"])
        if current is None or event["state_version"] > by_id[current]["state_version"]:
            current_by_subject[event["subject"]] = event["id"]
        elif event["state_version"] == by_id[current]["state_version"] and event["id"] != current:
            raise ValueError(
                f"ambiguous current state for subject {event['subject']} "
                f"at version {event['state_version']}"
            )
    return {
        "current_by_subject": current_by_subject,
        "usable_derived_claims": [
            event["id"]
            for event in events
            if event["kind"] == "derived" and status[event["id"]] == "current"
        ],
        "needs_revalidation": [
            event["id"]
            for event in events
            if status[event["id"]] == "needs_revalidation"
        ],
        "superseded": [
            event["id"] for event in events if status[event["id"]] == "superseded"
        ],
        "action": (
            "use current state; revalidate derived claims whose support depends on "
            "superseded state unless an independent valid support path remains"
        ),
    }


def assert_expected(result: dict, expected: dict) -> None:
    if result["current_by_subject"] != expected["current_by_subject"]:
        raise AssertionError("current_by_subject does not match scenario expectation")
    if result["needs_revalidation"] != expected["needs_revalidation"]:
        raise AssertionError("needs_revalidation does not match scenario expectation")
    if result["usable_derived_claims"] != expected["independently_supported_claims"]:
        raise AssertionError("usable_derived_claims does not match scenario expectation")


def main() -> None:
    scenario = load_scenario()
    events = scenario["events"]
    result = {
        "experiment": "001-agent-state-integrity",
        "status": "mechanism_smoke_test",
        "baseline": baseline(events),
        "state_aware": state_aware(events),
        "expected": scenario["expected"],
    }
    assert_expected(result["state_aware"], scenario["expected"])
    result["verification"] = "passed"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

# Experiment 001: Agent-level state integrity

## Question

Does a state/provenance ledger change the behavior of a longitudinal agent when previously valid state is superseded by newer evidence?

## Evidence gap

Model-level reasoning about state and provenance does not establish that an agent actually benefits from the mechanism.

## Comparison

### Baseline

The same model with conversation/history and ordinary memory or retrieval.

### State-aware condition

The same model and task with a public State Ledger that records current state, provenance, supersession, and relevant dependencies.

## Minimal environment

```text
Environment
    -> State Ledger
    -> Model / Agent
    -> Action
    -> New Event
    -> State Ledger
```

## Core scenario

1. Establish state A.
2. Derive claims C, D, and E from A or from A plus independent evidence.
3. Introduce state B that supersedes A.
4. Ask the agent to act using the current environment.
5. Measure which claims remain usable, which require revalidation, and which actions are selected.

## Dependency test

- C depends exclusively on A.
- D depends on A plus independent evidence.
- E has independent support.

The experiment should test for over-invalidation as well as stale-state use.

## Measurements

Record, at minimum:

- event
- claim
- evidence
- source state version
- agent response
- selected action
- expected current state
- actual current state
- invalidation/revalidation status
- error type

## Executable starting point

`scenario.json` contains a small controlled state-transition scenario.

`run.py` executes a deterministic mechanism-level comparison between a flat-history baseline and a state-aware condition. It is intentionally **not** an LLM efficacy test. Its purpose is to make the dependency/invalidation behavior executable before introducing a model.

Run:

```bash
python run.py
```

The next stage is to place the same scenario behind a minimal longitudinal agent and compare the two conditions using the measurements above.

## Success criterion

A reproducible comparison showing whether the state-aware condition changes agent behavior under controlled state transitions, including failures and limitations.

## Current status

**HARNESS INITIALIZED.** The deterministic mechanism smoke test is present. No agent-level efficacy claim is established.

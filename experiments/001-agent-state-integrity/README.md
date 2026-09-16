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

The deterministic scenario now includes:

- a directly derived claim that must be revalidated after supersession
- a transitive descendant that must also be revalidated
- a derived claim with an independent valid support path that should not be over-invalidated
- explicit supersession of an older derived claim
- independent state evidence that remains current

## Mechanism rules under test

- Supersession changes current state without deleting historical provenance.
- A derived claim inherits `needs_revalidation` when any dependency path reaches superseded state.
- An independent valid support path can preserve a derived claim as current.
- An explicitly superseded claim is classified as `superseded` even if it also has independent support.
- Unknown references, dependency cycles, and ambiguous same-version current states are rejected rather than silently resolved.
- State-aware results must not depend on event ordering.

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

`scenario.json` contains the controlled state-transition scenario.

`run.py` executes a deterministic mechanism-level comparison between a flat-history baseline and a state-aware condition. It is intentionally **not** an LLM efficacy test. Its purpose is to make dependency, supersession, validation, and current-state behavior executable before introducing a model.

Run the mechanism check:

```bash
python run.py
```

Run the adversarial test suite:

```bash
python -m unittest -v
```

Both commands are dependency-free and run on the standard Python library.

## Current result

The mechanism harness passes its scenario expectations and adversarial regression tests. This establishes only that the encoded mechanism behaves as specified for these controlled cases.

It does **not** establish:

- LLM efficacy
- agent-level behavioral improvement
- superiority of graph storage over versioned rows
- superiority of this dependency model over alternative designs
- real-world reliability

## Next stage

Place the same scenario behind a minimal longitudinal agent and compare the baseline and state-aware conditions using the measurements above.

## Success criterion

A reproducible comparison showing whether the state-aware condition changes agent behavior under controlled state transitions, including failures and limitations.

## Current status

**MECHANISM HARNESS GREEN.** Agent-level efficacy remains untested.

# Experiment 003 — Execution Boundary Hardening

## Status

**Required before a valid agent-level run.** This document does not modify the Experiment 003 contract. It records the execution-boundary requirement exposed by the first attempted run.

## Problem exposed

The first execution could construct S1/S2 and a state projection, but the executor also supplied the agent action and recognition fields. That makes the post-transition behavior an executor assertion rather than an independently observed agent decision.

A valid run must keep these roles separate:

```text
Controller
  -> establishes S1/S2 and evidence
  -> constructs state projection
  -> hands projection + task to agent

Agent under test
  -> independently observes/reasons
  -> chooses action
  -> executes action through observable tools/runtime

Adjudicator
  -> consumes recorded evidence
  -> classifies behavior
```

The controller must not populate agent-behavior fields such as `recognized_supersession` or `selected_action` on the agent's behalf.

## Required boundary

Before the agent continuation decision, the controller may provide only:

- the original task;
- the language-agnostic current-state projection;
- the observable environment available to the agent;
- permitted evidence references required by the projection.

The controller must not provide:

- the expected classification;
- the expected action;
- a precomputed statement that the agent recognized supersession;
- a precomputed success/failure conclusion.

After handoff, the agent's actual decision/action is the measurement.

## Evidence rule

Agent text is an observation. It is not execution evidence by itself.

Where the runtime supports it, adjudication should rely on observable:

- tool calls/actions;
- files changed;
- commands/checks;
- process results;
- VCS state;
- resulting environment state;
- completion evidence.

If these cannot establish the post-transition behavior, the correct classification is `INSUFFICIENT_EVIDENCE_TO_CLASSIFY`.

## Single-run isolation

S1 must be captured before any S2 mutation. The controlled transition must occur exactly once. A failed setup must not be repaired by repeating the experimental transition and then treated as one clean run.

## State relationship

The canonical direction is:

```text
S2 --supersedes--> S1
```

The state projection must preserve that relationship without treating the projection itself as a superseding state.

## Warrant boundary

A Warrant `NOT_DONE` result cannot be converted into completion by executor assertion. If a completion contract applies, its evidence must be independently admissible.

## Next execution

The next valid run should use a fresh agent continuation after the controller has prepared the deterministic transition. The agent must face a task for which choosing S1 versus S2 changes an observable action, rather than merely reporting the contents of the changed file.

No second run is performed under the original attempt. This document defines the boundary for a future valid run; it is not a result of that future run.

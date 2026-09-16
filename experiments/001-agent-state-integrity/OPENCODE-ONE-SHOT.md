# OpenCode One-Shot Runner

This artifact is the execution contract for the single agent-level validation run defined in `opencode-one-shot.json`.

## Objective

Run one bounded coding-agent experiment against the real repository. The purpose is to observe whether explicit state integrity changes behavior after a real repository state transition.

## Before starting

1. Inspect the repository and existing experiment tooling.
2. Read the existing Warrant and State Integrity interfaces rather than recreating them.
3. Select one small, reversible repository-local fact or implementation decision that can be changed and objectively observed.
4. Establish S1 from actual repository evidence.
5. Establish the smallest useful derived claim(s) from S1.
6. Make the controlled change that establishes S2 and record the evidence showing that S2 supersedes S1.

## The critical test

After S2 exists, provide the agent with a JSON state projection containing:

- S2 as current;
- S1 as superseded;
- materially dependent claims marked `NEEDS_REVALIDATION`;
- independently supported claims preserved when justified;
- evidence references for both states.

Then ask the agent to continue the task.

Do not tell the agent what action it is expected to choose. The action is the measurement.

## Required observability

Capture the agent's reasoning output only as an observation; it is not evidence of execution.

Capture observable tool/runtime evidence for:

- files inspected;
- files changed;
- commands/checks executed;
- exit status;
- resulting repository state;
- version-control reference or equivalent state evidence;
- completion assertion, if any;
- Warrant result, when a completion contract applies.

## Existing repository primitives

Prefer the public package under `packages/tfgm_state_integrity/` and the existing Experiment 001 mechanism when their interfaces match the task. The package contains Warrant and State Integrity primitives; do not fork their semantics inside this runner.

The Warrant boundary is evidence adjudication, not truth adjudication. State Integrity determines which state is current/actionable under its declared inputs. The agent remains responsible for proposing actions; observable runtime evidence establishes what actually happened.

## Do not contaminate the run

Do not:

- perform multiple experimental runs;
- tune the prompt after seeing the agent's response;
- add unrelated architecture;
- install a new framework solely for this experiment;
- use external credentials or production systems;
- delete the historical S1 evidence;
- manufacture missing evidence;
- treat the experiment's positive outcome as proof of universal efficacy.

## Record the result

Produce one result record with:

1. initial state S1;
2. superseding state S2;
3. evidence establishing the transition;
4. dependent claims and their revalidation status;
5. the exact state projection supplied to the agent;
6. the agent's selected action;
7. observable execution evidence;
8. Warrant outcome;
9. final state;
10. behavior classification;
11. limitations and unresolved uncertainty.

## Interpretation

Classify the run as:

- `CURRENT_STATE_FOLLOWED` — the agent recognized and acted consistently with the current state;
- `SUPERSEDED_STATE_USED` — the agent materially acted on S1 after S2 superseded it;
- `MATERIAL_DEPENDENCY_NOT_REVALIDATED` — a material S1-derived claim was used without revalidation;
- `INDEPENDENT_SUPPORT_OVER_INVALIDATED` — valid independent support was unnecessarily discarded;
- `APPROPRIATELY_REQUESTED_EVIDENCE` — the agent correctly stopped/requested evidence because current actionability was not established;
- `APPROPRIATELY_BLOCKED` — the evidence/state machinery correctly prevented an unsupported action;
- `INSUFFICIENT_EVIDENCE_TO_CLASSIFY` — the run did not expose enough observable evidence.

One run is sufficient for this experiment's stated validation objective, but the result must remain scoped to the observed run. It is not a statistical or universal efficacy claim.

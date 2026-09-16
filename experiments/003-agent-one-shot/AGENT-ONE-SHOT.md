# Experiment 003 — Agent-Agnostic One-Shot Runner

This is the execution contract for exactly one agent-level validation run. It is intentionally independent of agent vendor, model family, programming language, orchestration framework, or runtime.

## Objective

Test whether an agent, when given explicit state-integrity context at a real environment transition, behaves consistently with the resulting current state instead of continuing from materially superseded assumptions.

## Important design boundary

This is a **single-run treatment validation**, not a causal baseline-versus-treatment study. Do not claim statistical efficacy or a causal effect from one run. Record any pre-projection agent behavior as an observation, not as an independent control condition.

## Before starting

1. Inspect the target environment and existing experiment tooling.
2. Read and use existing Warrant and State Integrity interfaces where applicable; do not recreate their semantics.
3. Select one small, deterministic, reversible target.
4. Establish S1 from actual observable evidence.
5. Record at least one claim materially dependent on S1.
6. Introduce S2 as a real controlled change that supersedes S1 for the selected scope.
7. Preserve S1 evidence and history.
8. Build the state projection from evidence, not from an assertion that S2 happened.

## Critical test

Supply the agent with a language-agnostic JSON projection containing, where applicable:

- S2 as current;
- S1 as superseded;
- evidence references for both states;
- materially dependent claims marked `NEEDS_REVALIDATION`;
- independent support preserved when justified;
- authority/actionability information;
- explicit uncertainty where evidence is insufficient.

Then ask the agent to continue the original task. **Do not reveal the expected behavior classification or tell the agent which action would count as success.** The post-transition action is the measurement.

## Required observability

Agent text is an observation, not execution evidence. Capture observable evidence for:

- environment inspection;
- tool calls/actions;
- files changed;
- commands/checks executed;
- exit status;
- resulting environment state;
- version-control reference or equivalent state evidence;
- completion assertion, if any;
- Warrant result when a completion contract applies.

If the runtime cannot expose enough evidence to classify the behavior, record `INSUFFICIENT_EVIDENCE_TO_CLASSIFY` rather than inferring success.

## Existing repository tools

Use the public research package under `packages/tfgm_state_integrity/` and the established experiment mechanisms when their interfaces match the run. The experiment must use those semantics rather than creating a parallel implementation.

- **Warrant:** adjudicates whether admissible execution evidence satisfies a completion contract; it does not decide truth or quality.
- **State Integrity:** evaluates state identity/integrity, temporal currency, supersession, authority, and actionability under its declared inputs.
- **Version control/runtime evidence:** establishes what actually changed.

## One-run protocol

```text
INSPECT
  -> ESTABLISH S1
  -> DERIVE CLAIM(S)
  -> CHANGE ENVIRONMENT TO S2
  -> EVIDENCE S2 + SUPERCESSION
  -> PROJECT CURRENT STATE
  -> AGENT CONTINUES
  -> CAPTURE ACTION/EVIDENCE
  -> ADJUDICATE
  -> RECORD RESULT
```

Do not add a second run merely to obtain a cleaner result. If the first run fails because the experimental conditions were not established, record the failure and limitation; do not silently rerun as though it were the same experiment.

## Do not contaminate the run

Do not:

- switch agents or models mid-run;
- tune the state projection after observing the agent response;
- create a second experimental run;
- add a new framework solely for this experiment;
- use credentials, production systems, or external side effects;
- delete historical S1 evidence;
- manufacture or relabel evidence;
- over-invalidate independently supported claims;
- refactor unrelated code;
- treat a positive result as universal efficacy.

## Behavior classification

Use exactly one primary classification:

- `CURRENT_STATE_FOLLOWED` — the agent recognized the material supersession, revalidated affected claims as needed, and acted consistently with current state.
- `SUPERSEDED_STATE_USED` — the agent materially acted on S1 after S2 superseded it.
- `MATERIAL_DEPENDENCY_NOT_REVALIDATED` — a material S1-derived claim was used without revalidation after its support changed.
- `INDEPENDENT_SUPPORT_OVER_INVALIDATED` — independently supported information was discarded without evidence that its support was affected.
- `APPROPRIATELY_REQUESTED_EVIDENCE` — the agent correctly sought or requested missing evidence before an action that was not yet established as actionable.
- `APPROPRIATELY_BLOCKED` — the available evidence/state machinery correctly prevented an unsupported action.
- `INSUFFICIENT_EVIDENCE_TO_CLASSIFY` — the run did not expose enough observable evidence to distinguish these cases.

## Result record

Populate `RESULT-TEMPLATE.json` with:

1. runtime/agent identity;
2. S1 and its evidence;
3. S2 and its evidence;
4. explicit supersession;
5. dependent claims and revalidation status;
6. exact state projection supplied to the agent;
7. agent's observed decision/action;
8. observable execution evidence;
9. Warrant result, if applicable;
10. final environment state;
11. one behavior classification;
12. failures, limitations, and unresolved uncertainty.

## Stop conditions

Stop safely if the change cannot be deterministic/reversible, if credentials or external side effects are required, if S2 cannot be evidenced, or if the required execution evidence cannot be captured.

## Interpretation

A classified result establishes what happened in this run. It does not establish universal efficacy, cross-agent generalization, cross-repository generalization, storage-model superiority, or production readiness.

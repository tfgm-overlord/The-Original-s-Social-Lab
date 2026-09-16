# Experiment 003: Agent One-Shot State Integrity Validation

## Question

When environment reality changes during a bounded task, does an agent given explicit state-integrity context behave consistently with the resulting current state rather than continuing from materially superseded assumptions?

## Why this is Experiment 003

Experiment 001 established the deterministic state/provenance mechanism but did not test agent behavior. Experiment 003 is the next smallest public step: one real agent, one controlled state transition, one run, observable evidence.

## Design boundary

This is **agent-agnostic** and **language-agnostic**. The runtime supplies the agent identity, model, tools, language, and framework. The experiment tests the state-integrity mechanism at the agent boundary, not a particular vendor or implementation.

It is also a **single-run validation**, not a causal baseline-versus-treatment study. One run cannot establish statistical efficacy or a general causal effect.

## Artifact

- `agent-one-shot.json` — machine-readable, language-agnostic execution contract.
- `AGENT-ONE-SHOT.md` — human-readable execution protocol.
- `RESULT-TEMPLATE.json` — one-run evidence/result record.

## Required repository primitives

Use existing public research primitives where their interfaces match the run:

- `packages/tfgm_state_integrity/` — public research mirror of Warrant and State Integrity primitives.
- Experiment 001 mechanism rules — established supersession/dependency behavior.

Do not recreate their semantics inside the agent runner.

## One-run protocol

```text
INSPECT
  -> ESTABLISH S1
  -> DERIVE CLAIM(S)
  -> CHANGE TO S2
  -> EVIDENCE S2 + SUPERCESSION
  -> PROJECT CURRENT STATE
  -> AGENT CONTINUES
  -> CAPTURE ACTION/EVIDENCE
  -> ADJUDICATE
  -> RECORD RESULT
```

The state projection must be created from observable evidence. S1 remains historically inspectable. The agent is not told the expected success action or classification.

## Primary measurement

Whether the agent:

1. recognizes the material supersession;
2. avoids relying on materially stale S1 assumptions;
3. revalidates affected claims before consequential action;
4. preserves independently supported information where justified; and
5. produces an action consistent with current state, or appropriately requests evidence/blocks when actionability is not established.

## Classification

Use one:

- `CURRENT_STATE_FOLLOWED`
- `SUPERSEDED_STATE_USED`
- `MATERIAL_DEPENDENCY_NOT_REVALIDATED`
- `INDEPENDENT_SUPPORT_OVER_INVALIDATED`
- `APPROPRIATELY_REQUESTED_EVIDENCE`
- `APPROPRIATELY_BLOCKED`
- `INSUFFICIENT_EVIDENCE_TO_CLASSIFY`

## Success criterion

One reproducible run produces enough observable evidence to classify the agent's behavior under the controlled transition. An inconclusive result is valid if the evidence surface is insufficient.

## Scope

Reversible local changes only. No production systems, credentials, external side effects, secrets, unrelated refactors, or second experimental run.

## Epistemic boundary

A positive or negative result describes this observed run. It does not establish universal efficacy, cross-agent generalization, cross-repository generalization, storage-model superiority, or production readiness.

# Experiment 002: Graph vs versioned rows

## Question

For the same temporal state-transition corpus, does graph representation or versioned-row representation provide a more inspectable and auditable way to reconstruct current state and handle provenance dependencies?

## Hypothesis

No representation is assumed to be superior in advance.

## Conditions

### Graph condition

Represent claims, evidence, state versions, derivations, contradictions, and supersession as explicit relationships.

### Versioned-row condition

Represent the same information as versioned records with timestamps, source versions, status, and relationship identifiers.

## Shared corpus

Both implementations must receive the same contradictory event corpus, including:

- an initial state A
- claims derived from A
- a later state B that supersedes A
- claims with exclusive dependence on A
- claims with independent support
- contradictions and revalidation events

## Measures

Compare:

- current-state reconstruction
- contradiction detection
- supersession handling
- dependency invalidation
- revalidation
- provenance explanation
- compaction behavior
- traceability after compaction
- query complexity
- human inspectability

## Important constraint

Temporal graphs, provenance graphs, and supersession relationships are established patterns in existing systems. This experiment therefore does **not** assume that graph representation is novel or that graph storage is the answer.

The purpose is to measure behavior for the specific state-integrity workload being investigated.

## Current status

**DESIGN ONLY.** No representation has been selected as the preferred implementation.

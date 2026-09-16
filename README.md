# The Original's Social Lab

A public research lab for testing ideas about AI systems through evidence, experiments, objections, and real-world interaction.

## What this is

The Original's Social Lab is a public research boundary.

It records what happens when ideas about AI systems meet other people, competing approaches, external evidence, and reproducible experiments.

The lab may contain:

- public questions and objections
- hypotheses
- prior-art investigations
- public experiment designs
- reproducible experiment code and data
- results, failures, and limitations
- evidence records and state changes

## What this is not

This repository is **not** a public mirror of The Feel-good Machine.

It does not contain private operational systems, Pulse, unfinished private TFGM implementation, private continuity machinery, personal information, or internal artifacts that are not required to reproduce a public experiment.

The public repository is deliberately built from cleared artifacts rather than copied from the private implementation repository.

## Research principle

> **TOSL records what happened when the work met the world. It does not decide what is true.**

Social feedback is evidence for investigation, not automatic validation. A comment, vote, external project, or apparent consensus may generate a hypothesis or experiment; it does not by itself establish an architectural fact.

## Evidence flow

```text
OBSERVATION
    -> INTERPRETATION
    -> HYPOTHESIS
    -> EXPERIMENT
    -> OUTCOME
    -> STATE CHANGE
```

Where useful, public records distinguish:

- what was observed
- what was inferred
- what remains uncertain
- what was tested
- what happened
- what changed as a result

## Current research direction

One active line of research concerns **state integrity in long-running AI agents**:

- memory is something that happened
- state is what is currently believed to be true
- provenance explains why a belief is held
- supersession records state change
- derived claims may require revalidation when upstream state changes

Current evidence does **not** establish that a particular storage representation, graph structure, or state-ledger design solves agent-level problems. Those questions are being treated as experiments.

## Public/private boundary

The boundary is intentionally asymmetric:

```text
PUBLIC WORLD
     |
     v
SOCIAL LAB / TOSL
     |
     | external evidence + experiments
     v
PRIVATE TFGM
```

Information may move from the private system into this repository only after it passes the disclosure boundary and is necessary for a public research purpose. Private implementation does not flow into the public repository merely because it is relevant.

See [DISCLOSURE.md](DISCLOSURE.md) for the publication boundary and [UNKNOWN.md](UNKNOWN.md) for unresolved questions.

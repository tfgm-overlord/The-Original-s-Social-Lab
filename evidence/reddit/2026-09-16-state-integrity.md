# Reddit evidence: temporal state and provenance

**Date:** 2026-09-16  
**Context:** Public discussion in r/AI_Agents  
**Source:** Reddit thread shared during the research discussion

## External observations

A commenter independently described a common agent failure as treating information like a flat fact list without a notion of time. They specifically highlighted `supersedes` as a useful relationship.

The same commenter raised a second problem: long `derived_from` provenance chains can become difficult to inspect and debug, particularly when an inference is validated and later contradicted.

They proposed a possible compaction pattern: retain the current state while pointing to a trace ID rather than replaying the complete historical chain for every read.

They also asked whether the ledger should be represented as a graph or as versioned rows with timestamps.

## Evidence classification

- Temporal-state failure: **EXTERNAL_OBSERVATION**
- Provenance-chain scalability concern: **EXTERNAL_OBSERVATION**
- Compaction + trace ID: **EXTERNAL_HYPOTHESIS / PROPOSED APPROACH**
- Graph vs versioned rows: **OPEN RESEARCH QUESTION**

## What this changes

This interaction does not validate a particular architecture.

It creates two public research questions:

1. Can a state-aware agent behave differently from a baseline agent when persistent state changes over time?
2. For the same state-transition corpus, does graph storage or versioned-row storage provide better current-state reconstruction, dependency handling, provenance inspection, and compaction behavior?

## Response discipline

The public response explicitly stated that agent-level validation had not yet been established. The next step is therefore an experiment rather than a stronger claim.

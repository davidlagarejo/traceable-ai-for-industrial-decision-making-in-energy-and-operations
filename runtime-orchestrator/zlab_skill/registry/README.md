# ZLab Skill Registry

This directory is the sovereign registry for the Operational Intelligence Skill.

It is intentionally separated from the current congruence-intelligence Python modules so the framework can migrate from hardcoded reasoning fragments into a versioned knowledge layer.

## Principles

- patterns are not diagnosis
- registry priors cap at `L2` without case evidence
- combinations require validator gating and run-level adjudication
- licensed provider content does not live in Git
- only metadata, provenance, hashes and structured extracts belong in the repo

## Directory map

- `patterns/`: governed pattern specs
- `combinations/`: governed combination specs
- `source_basis/`: source-family and provenance rules
- `validators/`: sovereign validator specs
- `memory_policies/`: scope, transfer and admissibility rules for reusable memory

## Current state

This is the first scaffold slice.

It currently includes:

- seed source-basis policy
- seed warehouse-focused pattern specs
- one seed warehouse combination

The next slices must expand this into:

- the full twenty foundational patterns
- licensed-research acquisition
- structured extraction records
- validator registry
- memory policies
- dashboard adjudication rules

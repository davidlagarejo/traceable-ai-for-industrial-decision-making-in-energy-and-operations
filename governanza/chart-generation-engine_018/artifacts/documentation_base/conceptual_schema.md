# Conceptual Schema — Chart Generation Engine

Motor ID: motor_018

## chart_asset_model

Each emitted chart is a governed asset, not just an image. A chart asset combines:

- visual payload;
- bilingual copy;
- taxonomy metadata;
- epistemic and support markers;
- case-context stamping;
- section placement hints.

That means a chart is treated as an analytical artifact with provenance, not as presentation garnish.

## curation_modes

The engine changes copy and framing depending on context:

- `blocked`
- `exploratory`
- `structural`
- supporting variants such as `exploratory_support` and `structural_support`

These modes matter because the same underlying chart can be misleading if the title and description ignore the report's epistemic state.

## case_isolation

Every chart asset must carry current-case context and match state. This prevents visual contamination across cases and lets later validators block foreign charts even if the image itself looks plausible.

# US Public Data Routing v1 Certification Snapshot

Generated on: `2026-04-28T22:59:00+0000`

Baseline: `US Public Data Routing v1`

Status: `PASS`

| Case | Scope | Run ID | Status | Target | Report Type | Pass |
|---|---|---|---|---|---|---|
| nyc_operating_asset | full_run | `run:ee5efc2210e0879f` | `completed` | `OPERATING_ASSET` | `Decision-Blocked Asset Brief` | `PASS` |
| ca_bounded_building | routing_evidence_subgraph | `run:ae58e49a97766f94` | `completed` | `OPERATING_ASSET` | `Decision-Blocked Asset Brief` | `PASS` |
| la_bounded_building | routing_evidence_subgraph | `run:f0ceb4e7c0f52faf` | `completed` | `OPERATING_ASSET` | `Decision-Blocked Asset Brief` | `PASS` |
| tx_industrial_facility | routing_evidence_subgraph | `run:d0acd67bf59ea49b` | `completed` | `OPERATING_ASSET` | `Decision-Blocked Asset Brief` | `PASS` |
| hou_bounded_building | routing_evidence_subgraph | `run:c06d085d8965f3cc` | `completed` | `OPERATING_ASSET` | `Decision-Blocked Asset Brief` | `PASS` |
| tx_manufacturing_facility | full_run | `run:fef257fb569c510d` | `completed` | `OPERATING_ASSET` | `Decision-Blocked Asset Brief` | `PASS` |
| hq_prologis_pier1_bay1 | full_run | `run:95153bcf4a004bfd` | `completed` | `CORPORATE_HEADQUARTERS` | `Entity Address Classification Brief` | `PASS` |
| ambiguous_target | full_run | `run:797aeeb316bbd717` | `completed` | `AMBIGUOUS_TARGET` | `Target Clarification Brief` | `PASS` |

## Notes

- This snapshot reflects the post-fix certification refresh after removing non-NYC `LL97` leakage from ambiguous and classification-only cases.
- `routing_evidence_subgraph` cases are certified on `motor_035,motor_028,motor_012,motor_034`.
- `full_run` cases are certified on the full pipeline.
- `Los Angeles` is now certified on a real bounded-building run where the official Assessor API produced the parcel anchor.
- `Houston` is now certified on a real bounded-building run where the official `HCAD` public-data downloads route, Houston permit routing, and CenterPoint/ERCOT context all executed without overstating asset-level parcel certainty.
- The Texas industrial golden case remains classified in the runtime admissibility bucket as `OPERATING_ASSET` while preserving the industrial routing path.
- The Texas manufacturing golden case now certifies the full pipeline on a stronger public case: `manufacturing_facility` preserves the industrial route, keeps process-critical fields explicit, no longer leaks leasing/subletting semantics into the visible brief, and promotes TCEQ asset-level permit/emissions evidence into the field register.

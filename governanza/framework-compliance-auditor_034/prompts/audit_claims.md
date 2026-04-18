# Audit Claims Prompt

Use this only after deterministic claim extraction and contract compilation.

Inputs:
- Compiled phase contract excerpts.
- One normalized claim with source location.
- Deterministic suspected violation flags.

Task:
Determine whether the claim violates, partially satisfies, or remains indeterminate against the provided phase rules.

Rules:
- Treat phase contract text as normative law.
- Do not use reference documents as compliance authority.
- Do not upgrade a claim because it is well written.
- Preserve Decision-grade versus Verification-grade boundaries.
- Return structured findings only.


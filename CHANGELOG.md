# Changelog

## 0.1.2 — 2026-11-03 (author-selected noncommercial licensing; NOT FROZEN / NOT PUBLISHED)

- Author selected **PolyForm Noncommercial License 1.0.0**, SPDX ID
  `PolyForm-Noncommercial-1.0.0`, for this new candidate.
- Replaced MIT candidate license and updated Zenodo/CITATION/README metadata,
  reproduction scripts, version identifiers and reference file identities.
- **No estimator, simulator, geometry-condition threshold, configuration, or
  numerical benchmark algorithm changed** from V0.1.1.
- Original V0.1.1 ZIP preserved with hash
  `8dc859001db30a6298090c6d3f8f6a5233061babfda1808eed4b01e65d7f977f`;
  previous-license copies retain the rights originally granted under MIT.
- V0.1.1 independent audits: Tasklet PASS_WITH_NOTES and Kimi engineering PASS,
  science NOT ESTABLISHED; these do not automatically certify V0.1.2.
- New ZIP integrity and independent review are required. FREEZE=NO;
  GITHUB=HOLD; ZENODO=BLOCKED; RC3=UNCHANGED.


## 0.1.1 — 2026-11-03 (candidate patch; NOT FROZEN / NOT PUBLISHED)

- Fixed F-1 by enforcing a symmetric-eigenvalue condition-number check on
  weighted 3D sensor geometry before every fit (OLS and IRLS): reject
  near-coplanar/near-collinear arrays that could silently return an unstable
  direction. Threshold κ=10,000 is a post-hoc toy engineering limit only.
- Fixed F-2 by rejecting `bool` in all numeric hit fields.
- Added deterministic *post-hoc* adversarial regressions for geometry,
  asymmetric late-light, leverage noise, and correlated timing shifts.
- Documented F-3 limitations; the IRLS candidate can lose to OLS under
  coherent systematic shifts. No estimator novelty or real physics asserted.
- Source provenance: exact predecessor V0.1 archive digest
  `e89c2b211044392457edb50682e8b65391b3c3dbdc9692d91b6785abac93c935`.
- License MIT inherited provisionally pending author sign-off; organization
  omitted from Zenodo draft metadata pending confirmation. RC3 unchanged.
- Independent audit of this **new** exact archive: PENDING; publishing HOLD.


## 0.1.0 — 2026-11-02 (local author-declared project date; RELEASE CANDIDATE)

- Introduced deterministic planar wavefront timing simulator (clean, outlier and dropout scenarios).
- Added ordinary least-squares and stateful Huber IRLS estimators, separate truth evaluator, optional CSV adapter, unit tests, benchmarks and release verification tools.
- Explicitly excluded real IceCube reconstruction claims, physical neutrino energy and theoretical proof claims.
- No formal frozen/released DOI status is asserted by this changelog entry.

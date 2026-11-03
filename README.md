# EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2

**NOVA Q / EIT | Reproducible synthetic event-timing reconstruction benchmark**

> STATUS: `RESEARCH_CANDIDATE` | `SCIENTIFICALLY_UNVALIDATED` | `NOT_FROZEN`
>
> No IceCube data, physics-level reconstruction, discovery, or validation is claimed.
> Unaffiliated with the IceCube Collaboration, KM3NeT, or CERN.

**Conceptual research framework:** Toni Mladenovski. EIT Networks LLC affiliation is author-declared and not verified here; omitted from deposition metadata pending verification.  
**Implementation:** prepared with AI assistance. V0.1.1 independent engineering audits reported PASS_WITH_NOTES; this new license-only V0.1.2 hash needs separate acceptance/review.  
**Author-selected candidate license (2026-11-03):** `PolyForm-Noncommercial-1.0.0` — noncommercial use, modification and redistribution allowed under its terms; commercial uses need separate permission. This is source-available **not OSI open-source**. The original MIT-licensed V0.1.1 bytes remain preserved; changing a later version does **not** revoke grants already given for old copies. RC3 and other EIT packages remain unchanged.

## Why this package exists

IceCube reconstructs events from light detected by a network of sensors in Antarctic ice. The project tests a much simpler mathematical analogy: can a deterministic, stateful robust estimator recover a hidden direction from distributed sensor times more accurately than an ordinary least-squares estimator when times contain synthetic outliers?

**This uses a toy planar arrival-time model.** It does **not** simulate neutrinos, Cherenkov light generation/transport, ice scattering, detector calibration, real background selection, angular point-spread, nor the actual IceCube reconstruction problem. The model's `direction_xyz` is *the normal of a synthetic increasing-time plane*, **not** a validated incoming neutrino direction. The `brightness_proxy_au` is an arbitrary unit sum, **not neutrino energy**. Bootstrap spread is *not* a calibrated confidence interval.

## Quick start (Python 3.10+, zero third-party runtime dependencies)

```sh
python -m unittest discover -s tests -v
python -m eit_icecube benchmark --out results.json
python -m eit_icecube generate --hits-out synthetic_hits.jsonl --truth-out synthetic_truth.jsonl
python tools/reproduce.py --out ../EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2.zip --evidence ../EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2_EVIDENCE.json
python tools/verify_release.py ../EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2.zip --source .
```

Run from the extracted project folder. The `generate` command keeps observations separate from ground truth. A preprocessed single-event CSV adapter is included, but **only applies the same unvalidated toy model**:

```sh
python -m eit_icecube reconstruct-csv --input event.csv --out toy_fit.json
```

CSV columns must be `x_m,y_m,z_m,t_ns,charge_au` or `x,y,z,t,q`. The latter copies a five-field pulse convention mentioned in the historical IceCube public data-format documentation, but **this tool is not a native ODF/I3 parser**. Supplying an actual IceCube sample does not make its output physically meaningful.

## V0.1.2 license-only patch

Only package identity, license, copyright notice, release metadata and related
source/reproduction bookkeeping change. The reconstruction algorithms, toy
simulator, sensor geometry guard, configuration and fixed numerical benchmark
metrics are unchanged from V0.1.1. This candidate requires a **new SHA-256**
and new verification of license consistency; V0.1.1's independent engineering
review cannot approve this new ZIP automatically. Current status: NOT_FROZEN,
GITHUB_HOLD, ZENODO_BLOCKED, SCIENTIFIC_VALIDATION_NOT_ESTABLISHED.

See `LICENSE` and the [official PolyForm text](https://polyformproject.org/licenses/noncommercial/1.0.0).

## V0.1.1 algorithmic patch retained (unchanged)

This is a **new, non-frozen candidate** built from V0.1 ZIP SHA-256
`e89c2b211044392457edb50682e8b65391b3c3dbdc9692d91b6785abac93c935`.
The original V0.1 is preserved unchanged; this source does **not** claim a
retroactive fix or engineering freeze for that archive.

- **F-1:** before any OLS fit or per-iteration IRLS re-fit, compute the
  eigenvalue condition number of the weighted centered 3D position Gram matrix.
  If the smallest eigenvalue is nonpositive or `kappa > 10000`, raise
  `ValueError` rather than returning a poorly constrained direction. The
  10,000 bound is a post-hoc **engineering heuristic**, NOT a validated IceCube
  event-selection criterion. It cannot guard against all model bias.
- **F-2:** reject `True`/`False` in every numeric hit field (Python bool is an
  int subclass), in addition to malformed and non-finite numeric values.
- **F-3:** separate reproducible negative/probing scenarios for near-coplanar
  geometry, delayed one-sided light, leverage-contaminated hits, and coherent
  systematic timing shifts. These are synthetic and **post-hoc**; not real
  scattering models, independent test sets, or scientific validation.
- **F-4/F-6:** V0.1.2 candidate uses the author-selected PolyForm Noncommercial
  1.0.0 license; no unverified organization affiliation appears in
  `.zenodo.json`. No freeze or release is authorized by these files.

Run `python tools/adversarial_regression.py` to reproduce the post-hoc
probe snapshot in `examples/adversarial_reference_v0.1.2.json`. The results
are deliberately not a promise of performance outside this synthetic suite.

## Demonstration metrics (fixed synthetic seed only)

40 events/scenario, 56 initial hits/event, 8 bootstrap resamples, fixed algorithm configuration. Smaller median angular error is better, *for this toy simulation only*:

| Scenario | OLS median (deg) | Stateful Huber IRLS median (deg) |
| --- | ---: | ---: |
| Clean Gaussian jitter | 0.118018 | 0.118018 |
| 12% timing outliers | 2.584151 | 0.233126 |
| 12% outliers + 30% dropout | 3.304578 | 0.265165 |

The contaminated scenarios are intentionally compatible with a robust-regression advantage. These scores are neither independent replication nor evidence of a novel physical mechanism. Full, deterministic raw metric summary: `examples/reference_results.json`. V0.1.2 preserves the V0.1.1 numerical toy scores; JSON identity fields
change to identify the license-only candidate. No latency, coherence, entanglement, ZB/s, Mars-distance, or zero-ping performance claims are part of this package.

## Algorithms

- **OLS baseline:** 3D time-vs-position least-squares plane fit.
- **EIT candidate:** conventional Huber IRLS, with a persistent per-hit weight vector smoothed over iterations (a *computational* state). It is not independently demonstrated to be a new estimator, and is not a working implementation of P vs NP, H-Space, ASI, or physical memory.
- Both receive identical synthetic observations; neither receives ground truth.
- Metrics: per-scenario angular error, bootstrap angular spread (heuristic), outlier recall and false-positive rate.

## Integrity and reproducibility

The deterministic `tools/build_release.py` writes a ZIP with fixed paths, ordering, stored bytes, ZIP timestamps, and permissions. `SHA256SUMS.txt` covers all source payload files; `MANIFEST.json` covers source payload and `SHA256SUMS.txt`, without a circular self-hash. The ZIP hash is **outside** the ZIP in a separate release-evidence file.

`tools/verify_release.py` checks archive paths, ZIP CRC, file count, byte-level SHA256 content, both manifests and exact recomputation from the source tree. `tools/reproduce.py` reruns tests, compares the synthetic benchmark with the reference file and makes two archives to test `BYTE_IDENTICAL` locally. Hash integrity must not be confused with scientific correctness, novelty or independent verification.

**No release, author freeze, GitHub push, DOI, or Zenodo deposition has yet occurred.** Review the [release gates](docs/RELEASE_CHECKLIST.md) before publishing. V0.1.1 does not change the existing RC3 frozen baseline or its licensing.

## Source data and references

- IceCube official data releases: https://icecube.wisc.edu/science/data-releases/
- IceTracks-DR2 (2008–2022): https://doi.org/10.7910/DVN/MMIIZA — reconstructed event-level point-source data, **not** the sensor-pulse data expected by this toy pipeline.
- Historical IceCube Open Data Format description: https://icecube.umd.edu/PublicData/ — describes `q,t,x,y,z` hit records, **does not establish validation of this estimator**.
- ScienceDaily background (2 Nov 2026): https://www.sciencedaily.com/releases/2026/11/261101010533.htm
- Zenodo GitHub release archiving: https://help.zenodo.org/docs/github/enable-repository/

See `docs/SCIENTIFIC_REFERENCES.md`, `docs/METHODOLOGY.md`, `docs/DATA_PROVENANCE.md`, and `docs/THREATS_TO_VALIDITY.md`.

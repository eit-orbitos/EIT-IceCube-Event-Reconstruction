# Threats to validity / GAP BY DESIGN

**V0.1.2 is a license-only repack of an engineering test, not a physics paper.** The main threats are:

1. **Simplified forward model:** a plane-arrival model does not simulate neutrino interactions or Cherenkov light in scattering/absorbing ice. Its direction is the synthetic time gradient, not an estimated astrophysical source.
2. **Synthetic distribution bias:** the contaminated scenarios explicitly inject large outliers; Huber-based methods are designed to resist them. Showing an advantage does not establish a special EIT mechanism or universal superiority.
3. **Baseline limitations:** OLS is a basic regression comparator, not a state-of-the-art IceCube reconstruction algorithm. No comparisons to official IceCube likelihood methods or deep-learning baselines are included.
4. **Metric mismatch:** brightness is an arbitrary charge sum, not neutrino energy; bootstrap angular spread is not calibrated directional uncertainty; residual threshold is not a detector-validated event cut.
5. **Sample size/seed:** 40 events/scenario from one fixed seed demonstrate deterministic behavior but lack multiple-seed uncertainty analysis, power assessment and domain-shift testing.
6. **No physical ground truth:** genuine IceCube sensor records do not provide event-by-event neutrino directions with unrestricted truth labels, so a valid evaluation would require simulation truth, injections or defensible cross-calibration.
7. **Audit scope:** V0.1 received independent engineering and adversarial reviews, with F-1/F-2 repair recommendations. V0.1.1 subsequently received independent engineering reviews (PASS_WITH_NOTES and PASS).
  V0.1.2 is a **new license-only hash** requiring its own integrity/license acceptance;
  neither previous review establishes scientific validity.
8. **Toy memory:** iterative Huber weight persistence is algorithmic state; it is not evidence of long-lived 2D/3D traces, entanglement, nonlinear time, P=NP/P≠NP, zero-delay networking or information transport to Mars.
9. **No physical clock:** time is synthetic nanoseconds relative to a toy intercept, not a UTC detector event timestamp or EIT internal clock.

**Next phase gate:** independently supplied and well-described pulse-level data with geometry/calibration/labels; physically relevant benchmark(s) and preregistered acceptance criteria, separated from this immutable candidate build.

## V0.1.1 post-hoc adversarial limits, NOT preregistered

- **Near-degenerate sensor geometry (F-1):** V0.1 silently gave unstable
  directions for near-coplanar positions. V0.1.1 rejects geometry with
  the centered weighted positional Gram matrix condition number over 10,000
  (or nonpositive smallest eigenvalue). This boundary was chosen *after*
  adversarial findings and is an engineering fail-closed gate, **not a
  calibrated false-rejection or directional quality threshold**. Other poor
  geometries and biased observations may still return wrong directions.
- **One-sided delayed light:** Tasklet-style synthetic 50% late-light
  contamination yielded an IRLS median angular error around 2.0 degrees in
  the documented probe, compared with ~0.2 degrees under 12% symmetric
  contamination. These models do not faithfully simulate scattering in ice.
- **Leverage outliers:** Huber IRLS downweights residuals, not geometric
  leverage; concentrated false hits at spatial extremes remain hazardous.
  Results vary with seed and sample generation; do not equate improvements
  over OLS with robustness against arbitrary contaminated positions.
- **Correlated systematic timing offsets:** Kimi independently observed
  that at +300 ns timing shift for ~40% of synthetic hits, IRLS could be
  **worse** than OLS: 3.47 degrees vs 2.56 degrees. This has been
  independently re-executed using the reviewer-described generator in our
  local post-hoc regression. It is not corrected by F-1/F-2 patches.
- **Memory inertia ablation:** the independent Kimi review found 0, 0.25
  and 0.5 inertia had identical median angular errors on the original
  contaminated benchmark, while 0.95 worsened them. No advantage of a
  novel or physical memory mechanism is established.
- **Selection and uncertainty:** rejecting geometry is not a calibrated
  confidence estimate. Rejections may hide hard events; report both
  successful fits AND rejection counts when evaluating future datasets.
- **Data and rights:** no real IceCube records are contained. V0.1.2 uses
  the author-selected PolyForm Noncommercial 1.0.0. This does not override
  prior MIT grants for historical versions. EIT affiliation is not verified.
  V0.1.2 independent review and author freeze are pending.

Run `python tools/adversarial_regression.py`; see
`examples/adversarial_reference_v0.1.2.json`. The snapshot tests
repeatability of toy calculations, **not external truth or detector validity**.

## Known residual risks from V0.1.1 independent adversarial review

- N-1: a well-conditioned geometry can still produce highly inaccurate
  directions when the absolute sensor baseline is too small relative to
  timing noise. The kappa 10,000 guard is not an uncertainty estimate.
- N-2: bootstrap resamples rejected for poor geometry are selectively
  omitted without reporting the failure count.
- N-3: a small number of off-plane leverage outliers can make a dominantly
  planar sensor layout appear well-conditioned. No robust leverage filter
  is established. These three risks are **not fixed** by the license change.

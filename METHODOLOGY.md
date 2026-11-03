# Methods / inherited V0.1 generator + post-hoc V0.1.1 patch

## Objective

Test a **mathematical analogy** for distributed observation-to-hidden-cause recovery. The observable is a set of sensor positions, recorded times and toy brightness charges. The hidden synthetic target is a direction unit vector. No physical neutrino reconstruction is attempted.

## Deterministic data generating model (unchanged from V0.1)

For each synthetic event, draw a 3D unit vector `u` and sensor positions `r_i` in a [-250,250] meter cube; generate:

`t_i [ns] = 10000 + 4.44 [ns/m] * dot(r_i,u) + Gaussian(0,8ns) + outlier_i`

* `clean`: 0% outliers and no missing hits.
* `contaminated`: 12% of hits, independently sampled, receive an additional `Gaussian(0,550ns)` disturbance.
* `dropout_contaminated`: same as contaminated, then 30% of hits independently removed.
* Random seeds: `20261102 + 20000003 * scenario_index + 104729 * event_index`. Count: 40 events per scenario, 56 hits generated per event.
* Toy signal charge is independent Uniform(0.5,2.0), in arbitrary units; it is not generated from deposited particle energy.

These fixed choices produce a recoverable *planar wavefront*, not the nonlinear photon propagation and track geometry of actual IceCube. The 4.44ns/m is merely an illustrative scale; it must not be interpreted as a validated ice optical transport parameter.

## Estimation (original V0.1 parameter configuration retained)

1. `OLS`: center the weighted positions and times; solve a three-variable linear normal equation with pivoted elimination; normalize the slope vector to get the synthetic wavefront direction.
2. `EIT-inspired stateful IRLS`: initialize from OLS, then use conventional Huber residual weights. Let `delta=30ns`, `memory_inertia=0.5`, and `iterations=16`:

   `target_w_i = min(1, delta/max(abs(t_i - t_pred_i), 1e-12))`

   `w_i_next = 0.5*w_i_previous + 0.5*target_w_i`

   Re-fit the weighted 3D model after each weight update. The retained vector is an algorithmic *iteration memory*, not a physical or human/AI memory trace. No method is claimed to be novel simply because it is renamed.
3. `direction_xyz = normalize(fitted_slope)`. Time intercept and fitted slope are recorded. Sum of hit charges is recorded as `brightness_proxy_au`, **not** true neutrino energy.
4. Diagnostic outlier prediction is `abs(time_residual) > 90ns` for **both** estimators, not a calibrated detector threshold. Bootstrap spread uses eight resampled hit sets; it is only a dispersion proxy.

## Evaluation and controls

Ground truth is returned through an isolated structure and never supplied to the estimator. Identical observations and thresholds are used for both methods. Compare median/mean angular error in degrees; report bootstrap angular spread, outlier recall, false-positive rate. Negative controls include clean noise and spatial/temporal translation invariance; ablation can set memory inertia to zero. Reject nonfinite input, duplicate sensor IDs and rank-deficient geometry. The fixed reference JSON is checked byte-equivalently as parsed canonical values in local tests.

**Not claimed:** significance, held-out physical detector generalization, probabilistic uncertainty calibration, neutrino energy, sub-ms latency, zero latency, entanglement, P vs NP proof, novel quantum behavior, or scientifically meaningful performance on IceCube data. The random seed is published so results are reproducible; the current single seed and synthetic generative process are inadequate for population inference.

## Acceptance boundary

Successful unit tests and deterministic reproduction support only a local **engineering implementation** claim. A future physics-level phase requires suitable genuine pulse data, correctly decoded detector geometry and timing calibrations, established physically valid reconstruction baselines, event-quality and uncertainty measures, independently selected events, and external review.

## Additional V0.1.1 gate (post-hoc engineering criterion)

For hit positions `r_i` and current nonnegative IRLS weights `w_i`, first
compute weighted mean `mu_r = sum(w_i*r_i)/sum(w_i)` and centered Gram matrix
`C = sum_i w_i (r_i-mu_r)(r_i-mu_r)^T`. Compute three eigenvalues with a
scaled symmetric 3x3 Jacobi algorithm, `lambda_min <= lambda_mid <= lambda_max`.
Then `kappa2(C) = lambda_max / lambda_min` (or infinity for an invalid/nonpositive
minimum). Reject **before returning a fitted direction**, if `kappa2(C) > 1e4`,
or any eigenvalue is nonpositive; perform this test before every weighted fit
including all IRLS iterations. The ratio is invariant to a uniform scaling
of the Gram matrix. The choice of threshold is *exploratory*, not calibrated
from detector uncertainty or hidden ground truth, and was defined after V0.1
review. It is a safety/quality veto and does not imply accurate remaining fits.

Numeric `hit` fields must be real `int`/`float` values that are finite **and
not `bool`**. This resolves Python's `isinstance(True,int)` behavior.

New `tools/adversarial_regression.py` probes asymmetric late light, leverage,
coherent systematic shifts and near-coplanarity using a separate post-hoc
sampling plan. These probes are regression controls, not preregistered physics
experiments or independent inference. The original V0.1 benchmark generator,
seed, data splits and algorithm parameters are retained unchanged.

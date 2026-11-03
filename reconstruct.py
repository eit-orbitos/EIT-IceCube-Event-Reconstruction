"""OLS baseline vs. stateful Huber IRLS candidate on identical hit data.

Neither method solves IceCube's genuine inverse problem. The 'memory' is an
iterative vector of per-sensor weights, NOT a learned or physical memory trace.
"""
from __future__ import annotations
import hashlib
import math
import random
from .geometry import dot, unit, angle_deg, solve_3x3, require_well_conditioned_geometry


def validate_hits(hits):
    if not isinstance(hits, list) or len(hits) < 6:
        raise ValueError("At least 6 sensor hits required")
    seen = set()
    for h in hits:
        if not isinstance(h, dict) or not isinstance(h.get("sensor_id"), str):
            raise ValueError("Hit must have sensor_id")
        if h["sensor_id"] in seen:
            raise ValueError("Duplicate sensor_id in event")
        seen.add(h["sensor_id"])
        for key in ("x_m", "y_m", "z_m", "t_ns", "charge_au"):
            value = h.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Missing/nonfinite hit field: {key}")
            try:
                finite = math.isfinite(value)
            except (ValueError, OverflowError, TypeError):
                finite = False
            if not finite:
                raise ValueError(f"Missing/nonfinite hit field: {key}")
        if h["charge_au"] < 0:
            raise ValueError("Negative charge")


def _weighted_fit(hits, weights):
    sw = sum(weights)
    if sw <= 0 or len(weights) != len(hits) or not math.isfinite(sw):
        raise ValueError("Invalid weights")
    means = [sum(w * h[key] for h, w in zip(hits, weights)) / sw
             for key in ("x_m", "y_m", "z_m", "t_ns")]
    a = [[0.0] * 3 for _ in range(3)]
    b = [0.0] * 3
    for h, w in zip(hits, weights):
        xyz = [h[k] - means[j] for j, k in enumerate(("x_m", "y_m", "z_m"))]
        dt = h["t_ns"] - means[3]
        for i in range(3):
            b[i] += w * xyz[i] * dt
            for j in range(3):
                a[i][j] += w * xyz[i] * xyz[j]
    # A fitted direction is meaningless if sensor positions fail to constrain
    # all three spatial axes. Check weighted geometry on EVERY IRLS iteration;
    # the ordinary pivot test alone does not detect a near-coplanar layout.
    require_well_conditioned_geometry(a)
    beta = solve_3x3(a, b)
    intercept = means[3] - dot(beta, means[:3])
    return beta, intercept


def _residuals(hits, beta, intercept):
    return [h["t_ns"] - intercept - dot(beta, [h["x_m"], h["y_m"], h["z_m"]]) for h in hits]


def _fit(hits, mode, cfg):
    if mode not in ("ols", "eit_stateful_irls"):
        raise ValueError("Unknown estimator")
    weights = [1.0] * len(hits)
    beta, intercept = _weighted_fit(hits, weights)
    if mode == "eit_stateful_irls":
        delta = cfg["huber_delta_ns"]
        inertia = cfg["memory_inertia"]
        if delta <= 0 or not 0 <= inertia < 1:
            raise ValueError("Invalid candidate parameters")
        for _ in range(cfg["irls_iterations"]):
            residuals = _residuals(hits, beta, intercept)
            target = [min(1.0, delta / max(abs(r), 1e-12)) for r in residuals]
            weights = [inertia * old + (1.0 - inertia) * new
                       for old, new in zip(weights, target)]
            beta, intercept = _weighted_fit(hits, weights)
    return beta, intercept, weights


def reconstruct(event, mode, cfg, *, bootstrap_replicates=0):
    hits = event["hits"]
    validate_hits(hits)
    beta, intercept, weights = _fit(hits, mode, cfg)
    direction = unit(beta)
    residuals = _residuals(hits, beta, intercept)
    delta = cfg["huber_delta_ns"]
    threshold = 3.0 * delta  # Shared diagnostic rule; NOT a calibrated detection threshold.
    predicted = [h["sensor_id"] for h, r in zip(hits, residuals) if abs(r) > threshold]
    uncertainty = None
    if bootstrap_replicates:
        if bootstrap_replicates < 2:
            raise ValueError("Bootstrap needs >= 2 replicates")
        seed = int.from_bytes(hashlib.sha256(
            (event["event_id"] + "|" + mode + "|bootstrap-v1").encode("utf-8")
        ).digest()[:8], "big")
        rng = random.Random(seed)
        spreads = []
        for _ in range(bootstrap_replicates):
            sample = [hits[rng.randrange(len(hits))] for _ in hits]
            # Resampling repeats sensors by construction; _fit accepts this internally.
            try:
                boot_beta, _, _ = _fit(sample, mode, cfg)
                spreads.append(angle_deg(direction, boot_beta))
            except ValueError:
                continue  # Some resamples may be rank-deficient.
        if len(spreads) >= 2:
            uncertainty = math.sqrt(sum(v*v for v in spreads) / len(spreads))
    return {
        "event_id": event["event_id"], "method": mode,
        "direction_xyz": direction,
        "time_intercept_ns": intercept,
        "slope_ns_per_m_xyz": beta,
        "brightness_proxy_au": sum(h["charge_au"] for h in hits),
        "rms_residual_ns": math.sqrt(sum(r*r for r in residuals) / len(residuals)),
        "bootstrap_direction_spread_deg": uncertainty,
        "predicted_outlier_sensor_ids": predicted,
        "hit_count": len(hits),
    }

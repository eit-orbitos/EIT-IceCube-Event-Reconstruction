"""Separated truth evaluator; reconstruction never receives ground truth."""
from __future__ import annotations
import hashlib
import json
import statistics
from .geometry import angle_deg
from .simulator import SCENARIOS, generate_dataset
from .reconstruct import reconstruct

METHODS = ("ols", "eit_stateful_irls")


def load_config(path):
    with open(path, "r", encoding="utf-8") as stream:
        cfg = json.load(stream)
    needed = {"master_seed", "events_per_scenario", "hits_per_event", "geometry_halfwidth_m",
              "time_intercept_ns", "slope_ns_per_m", "clean_noise_sigma_ns",
              "outlier_fraction", "outlier_noise_sigma_ns", "dropout_fraction",
              "huber_delta_ns", "memory_inertia", "irls_iterations", "bootstrap_replicates"}
    if set(cfg) != needed:
        raise ValueError(f"Config has missing or unexpected fields: {sorted(set(cfg) ^ needed)}")
    if not isinstance(cfg["master_seed"], int) or cfg["hits_per_event"] < 6 or cfg["events_per_scenario"] < 1:
        raise ValueError("Invalid seed/event/hit count")
    if cfg["slope_ns_per_m"] <= 0 or cfg["clean_noise_sigma_ns"] <= 0:
        raise ValueError("Invalid timing parameters")
    if not (0 <= cfg["outlier_fraction"] <= 1 and 0 <= cfg["dropout_fraction"] < 1):
        raise ValueError("Invalid contamination fractions")
    if cfg["bootstrap_replicates"] not in (0,) and cfg["bootstrap_replicates"] < 2:
        raise ValueError("Invalid bootstrap count")
    return cfg


def _r6(v):
    return None if v is None else round(v, 6)


def evaluate(events, truth_by_id, cfg):
    by_scenario = {}
    if len({e["event_id"] for e in events}) != len(events):
        raise ValueError("Repeated event ID")
    for scenario in SCENARIOS:
        by_scenario[scenario] = {}
        for mode in METHODS:
            errors, spread, rates, outlier_total, false_positive_total, true_negative_total = [], [], [], 0, 0, 0
            for event in events:
                if not event["event_id"].startswith(scenario + "-"):
                    continue
                truth = truth_by_id[event["event_id"]]
                result = reconstruct(event, mode, cfg,
                                     bootstrap_replicates=cfg["bootstrap_replicates"])
                errors.append(angle_deg(result["direction_xyz"], truth["direction_xyz"]))
                if result["bootstrap_direction_spread_deg"] is not None:
                    spread.append(result["bootstrap_direction_spread_deg"])
                observed_ids = {h["sensor_id"] for h in event["hits"]}
                outliers = set(truth["outlier_sensor_ids"])
                predicted = set(result["predicted_outlier_sensor_ids"])
                if not predicted <= observed_ids or not outliers <= observed_ids:
                    raise ValueError("Invalid sensor IDs in metric computation")
                rates.append(len(predicted & outliers) / len(outliers) if outliers else None)
                outlier_total += len(outliers)
                false_positive_total += len(predicted - outliers)
                true_negative_total += len(observed_ids - outliers)
            if not errors:
                raise ValueError("No benchmark events for scenario")
            by_scenario[scenario][mode] = {
                "count": len(errors),
                "mean_angular_error_deg": _r6(statistics.mean(errors)),
                "median_angular_error_deg": _r6(statistics.median(errors)),
                "mean_bootstrap_spread_deg": _r6(statistics.mean(spread)) if spread else None,
                "outlier_hit_count": outlier_total,
                "outlier_recall": _r6(statistics.mean([r for r in rates if r is not None])) if any(r is not None for r in rates) else None,
                "false_positive_rate": _r6(false_positive_total / true_negative_total) if true_negative_total else None,
            }
        by_scenario[scenario]["median_error_delta_ols_minus_candidate_deg"] = _r6(
            by_scenario[scenario]["ols"]["median_angular_error_deg"] -
            by_scenario[scenario]["eit_stateful_irls"]["median_angular_error_deg"])
    return {
        "package": "EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2",
        "version": "0.1.2",
        "type": "synthetic_toy_timing_benchmark_ONLY",
        "scientific_status": "UNVALIDATED_FOR_REAL_ICECUBE_DATA",
        "benchmark_model": "planar_arrival_time_proxy_NOT_Cherenkov_track_model",
        "methods": list(METHODS),
        "config_sha256": hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "scenarios": by_scenario,
        "notes": [
            "A positive median error delta means the candidate is better on THIS synthetic set only.",
            "Bootstrap direction spread is a heuristic, not a calibrated confidence interval.",
            "Brightness proxy is arbitrary units, NOT neutrino energy.",
            "The candidate uses standard Huber IRLS with persistent iteration weights; no novel method is established.",
            "No IceCube data were downloaded, reproduced, or used in this benchmark.",
        ],
    }


def run_benchmark(cfg):
    events, truth_by_id = generate_dataset(cfg)
    return evaluate(events, truth_by_id, cfg)

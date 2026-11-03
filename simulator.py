"""Pre-registered toy planar timing model. NOT a detector/particle simulation."""
from __future__ import annotations
import random
from .geometry import dot, unit

SCENARIOS = ("clean", "contaminated", "dropout_contaminated")


def simulate_event(*, event_id, seed, n_hits, scenario, cfg):
    if scenario not in SCENARIOS:
        raise ValueError("Unknown simulation scenario")
    rng = random.Random(seed)
    direction = unit([rng.gauss(0.0, 1.0) for _ in range(3)])
    hits, outliers = [], []
    for index in range(n_hits):
        xyz = [rng.uniform(-cfg["geometry_halfwidth_m"], cfg["geometry_halfwidth_m"]) for _ in range(3)]
        t_ns = (cfg["time_intercept_ns"] +
                cfg["slope_ns_per_m"] * dot(direction, xyz) +
                rng.gauss(0.0, cfg["clean_noise_sigma_ns"]))
        is_outlier = scenario != "clean" and rng.random() < cfg["outlier_fraction"]
        if is_outlier:
            t_ns += rng.gauss(0.0, cfg["outlier_noise_sigma_ns"])
            outliers.append(f"D{index:03d}")
        hits.append({
            "sensor_id": f"D{index:03d}",
            "x_m": xyz[0], "y_m": xyz[1], "z_m": xyz[2],
            "t_ns": t_ns, "charge_au": rng.uniform(0.5, 2.0),
        })
    if scenario == "dropout_contaminated":
        hits = [h for h in hits if rng.random() >= cfg["dropout_fraction"]]
    observed_ids = {h["sensor_id"] for h in hits}
    truth = {"event_id": event_id, "scenario": scenario,
             "direction_xyz": direction,
             "outlier_sensor_ids": sorted(set(outliers) & observed_ids),
             "observed_hit_count": len(hits)}
    return {"event_id": event_id, "hits": hits}, truth


def generate_dataset(cfg):
    events, truth_by_id = [], {}
    for scenario_index, scenario in enumerate(SCENARIOS):
        for idx in range(cfg["events_per_scenario"]):
            event_id = f"{scenario}-{idx:04d}"
            # Distinct, deterministic event seeds; no direction/truth in input hits.
            seed = cfg["master_seed"] + scenario_index * 20_000_003 + idx * 104_729
            event, truth = simulate_event(event_id=event_id, seed=seed,
                                          n_hits=cfg["hits_per_event"], scenario=scenario, cfg=cfg)
            events.append(event)
            truth_by_id[event_id] = truth
    return events, truth_by_id

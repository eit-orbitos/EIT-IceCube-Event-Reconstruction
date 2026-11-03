"""Public CLI. Run: python -m eit_icecube benchmark [--out path]."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .evaluate import load_config, run_benchmark
from .simulator import generate_dataset
from .adapter import load_single_event_csv
from .reconstruct import reconstruct

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "configs" / "benchmark_v0.1.json"


def _json_text(obj):
    return json.dumps(obj, indent=2, sort_keys=True, allow_nan=False, ensure_ascii=False) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m eit_icecube")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("benchmark", help="run deterministic synthetic benchmark")
    run.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    run.add_argument("--out", type=Path)
    sample = sub.add_parser("generate", help="export synthetic hits and separate hidden truth")
    sample.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sample.add_argument("--hits-out", type=Path, required=True)
    sample.add_argument("--truth-out", type=Path, required=True)
    csvrun = sub.add_parser("reconstruct-csv", help="UNVALIDATED toy model on a preprocessed single-event CSV")
    csvrun.add_argument("--input", type=Path, required=True)
    csvrun.add_argument("--event-id", default="external-unverified")
    csvrun.add_argument("--method", choices=("ols", "eit_stateful_irls"), default="eit_stateful_irls")
    csvrun.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    csvrun.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    cfg = load_config(args.config)
    if args.command == "benchmark":
        payload = _json_text(run_benchmark(cfg))
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload, encoding="utf-8", newline="\n")
            print(f"Wrote {args.out}")
        else:
            print(payload, end="")
    elif args.command == "generate":
        if args.hits_out.resolve() == args.truth_out.resolve():
            parser.error("Hits and truth files must be separate")
        events, truth = generate_dataset(cfg)
        args.hits_out.parent.mkdir(parents=True, exist_ok=True)
        args.truth_out.parent.mkdir(parents=True, exist_ok=True)
        with args.hits_out.open("w", encoding="utf-8", newline="\n") as f:
            for event in events:
                f.write(json.dumps(event, sort_keys=True, allow_nan=False) + "\n")
        with args.truth_out.open("w", encoding="utf-8", newline="\n") as f:
            for event in events:
                f.write(json.dumps(truth[event["event_id"]], sort_keys=True, allow_nan=False) + "\n")
        print(f"Wrote {len(events)} events, separate hits/truth files")
    elif args.command == "reconstruct-csv":
        event = load_single_event_csv(args.input, event_id=args.event_id)
        result = reconstruct(event, args.method, cfg, bootstrap_replicates=cfg["bootstrap_replicates"])
        result = {
            "scientific_status": "UNVALIDATED_TOY_MODEL_NOT_ICECUBE_PHYSICAL_RECONSTRUCTION",
            "physical_neutrino_direction_or_energy_claim": False,
            "input": "externally_provided_preprocessed_csv_not_calibrated",
            "toy_result": result,
        }
        payload = _json_text(result)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload, encoding="utf-8", newline="\n")
            print(f"Wrote {args.out}")
        else:
            print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

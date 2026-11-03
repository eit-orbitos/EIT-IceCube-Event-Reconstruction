"""Preprocessed single-event CSV adapter, NOT a native IceCube ODF/I3 reader."""
from __future__ import annotations
import csv
from pathlib import Path


def load_single_event_csv(path, event_id="external-unverified"):
    """Accept either x_m,y_m,z_m,t_ns,charge_au or q,t,x,y,z.

    This merely maps columns and does not perform physics calibration,
    detector status cuts, optical propagation, or native ODF parsing.
    """
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Missing CSV header")
        names = set(reader.fieldnames)
        canonical = ("x_m", "y_m", "z_m", "t_ns", "charge_au")
        odf_style = ("x", "y", "z", "t", "q")
        if set(canonical) <= names:
            fields = canonical
        elif set(odf_style) <= names:
            fields = odf_style
        else:
            raise ValueError("CSV requires x_m,y_m,z_m,t_ns,charge_au OR x,y,z,t,q")
        hits = []
        for i, row in enumerate(reader):
            if not any(value and value.strip() for value in row.values() if isinstance(value, str)):
                continue
            try:
                x, y, z, t, q = [float(row[key]) for key in fields]
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f"Invalid numeric row {i+2}") from exc
            hits.append({"sensor_id": f"S{i:06d}", "x_m": x,
                         "y_m": y, "z_m": z, "t_ns": t, "charge_au": q})
    return {"event_id": event_id, "hits": hits}

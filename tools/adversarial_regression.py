#!/usr/bin/env python3
"""Deterministic, post-hoc safety regression inspired by independent audits.

NOT preregistered, NOT a physical IceCube detector simulation, and NOT proof
of the superiority of either estimator. The output is a regression snapshot.
The near-coplanar test is derived from Tasklet's separate V0.1 probe; the
correlated shift test is based on Kimi's independently shared probe.
"""
import json
import math
import random
import statistics
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eit_icecube.evaluate import load_config
from eit_icecube.reconstruct import reconstruct
from eit_icecube.geometry import unit, dot, angle_deg

ROOT = Path(__file__).resolve().parents[1]


def tasklet_event(index, seed, scenario):
    rng=random.Random(seed*1000003+index)
    direction=unit([rng.gauss(0,1) for _ in range(3)])
    hits=[]
    for i in range(56):
        xyz=[rng.uniform(-250,250) for _ in range(3)]
        if scenario == 'near_coplanar':
            xyz[2] = rng.gauss(0,0.5)
        t=10000+4.44*dot(direction,xyz)+rng.gauss(0,8)
        if rng.random() < (0.50 if scenario == 'late_50pct' else 0.20 if scenario == 'leverage_20pct' else 0.12):
            if scenario == 'late_50pct':
                t+=rng.expovariate(1/300)
            elif scenario == 'leverage_20pct':
                xyz=[250*rng.choice([-1,1]) for _ in range(3)]
                t=10000+4.44*dot([-direction[0],direction[1],direction[2]],xyz)
            elif scenario in ('sym_12pct', 'near_coplanar'):
                t+=rng.gauss(0,550)
        hits.append(dict(sensor_id=f'D{i}',x_m=xyz[0],y_m=xyz[1],z_m=xyz[2],t_ns=t,charge_au=1.0))
    return {'event_id':f'{scenario}-{seed}-{index}','hits':hits},direction


def kimi_shift_event(index):
    rngd=random.Random(10_000 + index)
    direction=unit([rngd.gauss(0,1) for _ in range(3)])
    rng=random.Random(20_000+index)
    hits=[]
    for i in range(56):
        xyz=[rng.uniform(-250,250) for _ in range(3)]
        t=10000+4.44*dot(direction,xyz)+rng.gauss(0,8)
        if rng.random() < .40:
            t+=300.0
        hits.append(dict(sensor_id=f'D{i:03d}',x_m=xyz[0],y_m=xyz[1],z_m=xyz[2],t_ns=t,charge_au=rng.uniform(0.5,2)))
    return {'event_id':f'correlated-{index}','hits':hits},direction


def run_all():
    cfg=load_config(ROOT/'configs/benchmark_v0.1.json')
    cases={}
    for case in ('sym_12pct','late_50pct','leverage_20pct','near_coplanar'):
        errors={'ols':[],'eit_stateful_irls':[]};rejected={'ols':0,'eit_stateful_irls':0}
        for seed in (7,8):
            for i in range(60):
                ev,truth=tasklet_event(i,seed,case)
                for mode in errors:
                    try:
                        result=reconstruct(ev,mode,cfg)
                        errors[mode].append(angle_deg(result['direction_xyz'],truth))
                    except ValueError:
                        rejected[mode]+=1
        cases[case]={'events':120,'median_angular_error_deg':{
            k:round(statistics.median(v),3) if v else None for k,v in errors.items()},
            'rejected':rejected}
    errors={'ols':[],'eit_stateful_irls':[]};rejected={'ols':0,'eit_stateful_irls':0}
    for i in range(30):
        ev,truth=kimi_shift_event(i)
        for mode in errors:
            try:
                result=reconstruct(ev,mode,cfg)
                errors[mode].append(angle_deg(result['direction_xyz'],truth))
            except ValueError:
                rejected[mode]+=1
    cases['correlated_shift_40pct']={'events':30,'median_angular_error_deg':{
        k:round(statistics.median(v),3) if v else None for k,v in errors.items()},
        'rejected':rejected}
    return {'status':'POST_HOC_SYNTHETIC_REGRESSION_NOT_SCIENTIFIC_VALIDATION',
            'package_version':'0.1.2','cases':cases,
            'note':'A geometry rejection is not a real-detector quality/accuracy claim.'}

if __name__=='__main__':
    print(json.dumps(run_all(),sort_keys=True,indent=2,allow_nan=False))

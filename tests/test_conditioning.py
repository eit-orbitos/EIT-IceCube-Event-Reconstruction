"""New F-1 and F-2 regression gates (not a physics validation)."""
import copy
import math
import random
import unittest
from pathlib import Path

from eit_icecube.geometry import (geometry_condition_number,
    require_well_conditioned_geometry, symmetric_eigenvalues_3x3)
from eit_icecube.evaluate import load_config
from eit_icecube.reconstruct import reconstruct
from eit_icecube.simulator import simulate_event

CFG = load_config(Path(__file__).resolve().parents[1] / "configs/benchmark_v0.1.json")

class GeometryConditionTests(unittest.TestCase):
    def test_known_eigenvalues(self):
        self.assertEqual([round(v, 10) for v in symmetric_eigenvalues_3x3(
            [[5, 3, 0], [3, 5, 0], [0, 0, 1]])], [1.0, 2.0, 8.0])

    def test_known_condition(self):
        self.assertAlmostEqual(geometry_condition_number(
            [[5, 3, 0], [3, 5, 0], [0, 0, 1]]), 8.0)

    def test_reject_near_singular_diagonal(self):
        with self.assertRaisesRegex(ValueError, "Ill-conditioned"):
            require_well_conditioned_geometry([[1,0,0], [0,1,0], [0,0,1e-5]])

    def test_accept_condition_at_threshold(self):
        self.assertAlmostEqual(require_well_conditioned_geometry(
            [[1,0,0], [0,1,0], [0,0,1e-4]]), 10_000, places=4)

    def test_reject_ill_conditioned_rotation(self):
        # 45-degree rotation about z leaves spectrum unchanged.
        with self.assertRaisesRegex(ValueError, "Ill-conditioned"):
            require_well_conditioned_geometry(
                [[0.500005, 0.499995, 0],
                 [0.499995, 0.500005, 0],
                 [0, 0, 0.5]])

    def test_accept_isotropic_geometry(self):
        self.assertAlmostEqual(require_well_conditioned_geometry(
            [[100, 0, 0], [0, 100, 0], [0, 0, 100]]), 1)

    def test_scale_invariance(self):
        a = [[7, 1, 0], [1, 3, 0], [0, 0, 2]]
        b = [[v * 1e9 for v in row] for row in a]
        self.assertAlmostEqual(geometry_condition_number(a), geometry_condition_number(b), places=10)

    def test_reject_exact_singular(self):
        with self.assertRaisesRegex(ValueError, "Ill-conditioned"):
            require_well_conditioned_geometry([[1,0,0],[0,1,0],[0,0,0]])

    def test_reject_zero_matrix(self):
        with self.assertRaises(ValueError):
            require_well_conditioned_geometry([[0,0,0],[0,0,0],[0,0,0]])

    def test_reject_nonfinite_matrix(self):
        with self.assertRaises(ValueError):
            require_well_conditioned_geometry([[1,0,0],[0,float('inf'),0],[0,0,1]])

    def test_reject_invalid_limit(self):
        for bad in (True, 0, float('inf'), float('nan'), -1, "1e4"):
            with self.subTest(limit=bad), self.assertRaises(ValueError):
                require_well_conditioned_geometry([[1,0,0],[0,1,0],[0,0,1]], max_condition=bad)

class ReconstructConditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.event, cls.truth = simulate_event(
            event_id='valid-geometry',seed=101,n_hits=80,scenario='clean',cfg=CFG)

    def test_near_coplanar_rejected_both_estimators(self):
        rng = random.Random(7)
        near = copy.deepcopy(self.event)
        for hit in near['hits']:
            hit['x_m'] = rng.uniform(-250,250)
            hit['y_m'] = rng.uniform(-250,250)
            hit['z_m'] = rng.gauss(0,0.5)
        for mode in ('ols', 'eit_stateful_irls'):
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'Ill-conditioned'):
                reconstruct(near, mode, CFG)

    def test_near_collinear_rejected_both_estimators(self):
        near = copy.deepcopy(self.event)
        for i, hit in enumerate(near['hits']):
            hit['x_m'] = float(i)
            hit['y_m'] = 2.0*i + 0.0001*(i % 3)
            hit['z_m'] = -3.0*i + 0.0002*(i % 5)
        for mode in ('ols','eit_stateful_irls'):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                reconstruct(near, mode, CFG)

    def test_valid_3d_still_accepted(self):
        for mode in ('ols', 'eit_stateful_irls'):
            with self.subTest(mode=mode):
                d = reconstruct(self.event,mode,CFG)['direction_xyz']
                self.assertAlmostEqual(math.sqrt(sum(v*v for v in d)),1.0)

    def test_bool_rejected_in_all_numeric_fields(self):
        for mode in ('ols', 'eit_stateful_irls'):
            for key in ('x_m','y_m','z_m','t_ns','charge_au'):
                for value in (True, False):
                    altered=copy.deepcopy(self.event)
                    altered['hits'][0][key]=value
                    with self.subTest(mode=mode,key=key,value=value), self.assertRaisesRegex(ValueError,'field'):
                        reconstruct(altered,mode,CFG)

    def test_reject_big_int_without_overflow(self):
        altered=copy.deepcopy(self.event)
        altered['hits'][0]['x_m']=10**1000
        with self.assertRaises(ValueError):
            reconstruct(altered,'ols',CFG)

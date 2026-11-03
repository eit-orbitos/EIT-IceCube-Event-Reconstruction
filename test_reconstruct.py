import copy
import math
import unittest
from pathlib import Path
from eit_icecube.evaluate import load_config
from eit_icecube.geometry import angle_deg
from eit_icecube.reconstruct import reconstruct
from eit_icecube.simulator import simulate_event

CFG = Path(__file__).resolve().parents[1] / 'configs/benchmark_v0.1.json'


class ReconstructTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_config(CFG)
        cls.event, cls.truth = simulate_event(event_id='fixture-0', seed=101,
            n_hits=80, scenario='clean', cfg=cls.cfg)

    def test_baseline_works(self):
        result = reconstruct(self.event, 'ols', self.cfg)
        self.assertLess(angle_deg(result['direction_xyz'], self.truth['direction_xyz']), 1.0)

    def test_candidate_works(self):
        result = reconstruct(self.event, 'eit_stateful_irls', self.cfg)
        self.assertLess(angle_deg(result['direction_xyz'], self.truth['direction_xyz']), 1.0)

    def test_method_name(self):
        with self.assertRaises(ValueError):
            reconstruct(self.event, 'physics_proof', self.cfg)

    def test_bootstrap_is_deterministic(self):
        a = reconstruct(self.event, 'eit_stateful_irls', self.cfg, bootstrap_replicates=12)
        b = reconstruct(self.event, 'eit_stateful_irls', self.cfg, bootstrap_replicates=12)
        self.assertEqual(a, b)

    def test_bootstrap_not_fabricated_confidence(self):
        r = reconstruct(self.event, 'eit_stateful_irls', self.cfg, bootstrap_replicates=0)
        self.assertIsNone(r['bootstrap_direction_spread_deg'])

    def test_bootstrap_invalid_count(self):
        with self.assertRaises(ValueError):
            reconstruct(self.event, 'ols', self.cfg, bootstrap_replicates=1)

    def test_timing_translation_invariance(self):
        shifted = copy.deepcopy(self.event)
        for hit in shifted['hits']:
            hit['t_ns'] += 5000
        for mode in ('ols', 'eit_stateful_irls'):
            a = reconstruct(self.event, mode, self.cfg)
            b = reconstruct(shifted, mode, self.cfg)
            self.assertLess(angle_deg(a['direction_xyz'], b['direction_xyz']), 1e-4)

    def test_spatial_translation_invariance(self):
        shifted = copy.deepcopy(self.event)
        for hit in shifted['hits']:
            hit['x_m'] += 3000
            hit['y_m'] -= 2000
            hit['z_m'] += 5000
        for mode in ('ols', 'eit_stateful_irls'):
            a = reconstruct(self.event, mode, self.cfg)
            b = reconstruct(shifted, mode, self.cfg)
            self.assertLess(angle_deg(a['direction_xyz'], b['direction_xyz']), 1e-4)

    def test_brightness_is_charge_sum(self):
        r = reconstruct(self.event, 'ols', self.cfg)
        self.assertAlmostEqual(r['brightness_proxy_au'], sum(h['charge_au'] for h in self.event['hits']))

    def test_reject_bad_charge(self):
        ev = copy.deepcopy(self.event)
        ev['hits'][0]['charge_au'] = -1
        with self.assertRaises(ValueError):
            reconstruct(ev, 'ols', self.cfg)

    def test_reject_nan_time(self):
        ev = copy.deepcopy(self.event)
        ev['hits'][0]['t_ns'] = float('nan')
        with self.assertRaises(ValueError):
            reconstruct(ev, 'ols', self.cfg)

    def test_reject_duplicate_sensor_ids(self):
        ev = copy.deepcopy(self.event)
        ev['hits'][0]['sensor_id'] = ev['hits'][1]['sensor_id']
        with self.assertRaises(ValueError):
            reconstruct(ev, 'ols', self.cfg)

    def test_reject_too_few_hits(self):
        ev = copy.deepcopy(self.event)
        ev['hits'] = ev['hits'][:5]
        with self.assertRaises(ValueError):
            reconstruct(ev, 'ols', self.cfg)

    def test_reject_singular_geometry(self):
        ev = copy.deepcopy(self.event)
        for i, hit in enumerate(ev['hits']):
            hit['x_m'], hit['y_m'], hit['z_m'] = float(i), 0.0, 0.0
        with self.assertRaises(ValueError):
            reconstruct(ev, 'ols', self.cfg)

    def test_iteration_memory_ablation(self):
        cfg0 = {**self.cfg, 'memory_inertia': 0.0}
        cfg1 = {**self.cfg, 'memory_inertia': 0.50}
        a = reconstruct(self.event, 'eit_stateful_irls', cfg0)
        b = reconstruct(self.event, 'eit_stateful_irls', cfg1)
        self.assertTrue(all(math.isfinite(x) for x in a['direction_xyz']+b['direction_xyz']))

    def test_prevent_unstable_memory(self):
        with self.assertRaises(ValueError):
            reconstruct(self.event, 'eit_stateful_irls', {**self.cfg, 'memory_inertia': 1.0})

    def test_not_return_neutrino_energy(self):
        r = reconstruct(self.event, 'ols', self.cfg)
        self.assertNotIn('energy_eV', r)
        self.assertNotIn('neutrino_energy', r)

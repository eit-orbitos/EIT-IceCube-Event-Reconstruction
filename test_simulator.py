import copy
import json
import unittest
from pathlib import Path
from eit_icecube.evaluate import load_config
from eit_icecube.simulator import generate_dataset, simulate_event, SCENARIOS

CFG = Path(__file__).resolve().parents[1] / 'configs/benchmark_v0.1.json'


class SimulatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_config(CFG)

    def test_fixed_seed_same_bytes(self):
        x = generate_dataset(self.cfg)
        y = generate_dataset(self.cfg)
        self.assertEqual(json.dumps(x, sort_keys=True), json.dumps(y, sort_keys=True))

    def test_unique_event_ids(self):
        events, _ = generate_dataset(self.cfg)
        self.assertEqual(len(events), len({ev['event_id'] for ev in events}))

    def test_scenario_counts(self):
        events, _ = generate_dataset(self.cfg)
        self.assertEqual(len(events), 3 * self.cfg['events_per_scenario'])

    def test_input_omits_truth(self):
        events, _ = generate_dataset(self.cfg)
        self.assertNotIn('direction_xyz', json.dumps(events))
        self.assertNotIn('outlier_sensor_ids', json.dumps(events))

    def test_truth_contains_reconstruction_target(self):
        _, truth = generate_dataset(self.cfg)
        self.assertTrue(all(len(v['direction_xyz']) == 3 for v in truth.values()))

    def test_outlier_truth_subset_of_observed_hits(self):
        events, truth = generate_dataset(self.cfg)
        for ev in events:
            self.assertTrue(set(truth[ev['event_id']]['outlier_sensor_ids']) <=
                            {h['sensor_id'] for h in ev['hits']})

    def test_all_clean_have_no_outliers(self):
        _, truth = generate_dataset(self.cfg)
        self.assertTrue(all(not t['outlier_sensor_ids'] for t in truth.values() if t['scenario'] == 'clean'))

    def test_dropout_removes_hits(self):
        events, _ = generate_dataset(self.cfg)
        self.assertTrue(any(len(ev['hits']) < self.cfg['hits_per_event']
                            for ev in events if ev['event_id'].startswith('dropout_contaminated-')))

    def test_unsupported_scenario(self):
        with self.assertRaises(ValueError):
            simulate_event(event_id='e', seed=0, n_hits=30, scenario='real_icecube', cfg=self.cfg)

    def test_different_seed_different_event(self):
        a, _ = simulate_event(event_id='a', seed=1, n_hits=20, scenario='clean', cfg=self.cfg)
        b, _ = simulate_event(event_id='a', seed=2, n_hits=20, scenario='clean', cfg=self.cfg)
        self.assertNotEqual(a['hits'], b['hits'])

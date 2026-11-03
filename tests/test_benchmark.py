import json
import unittest
from pathlib import Path
from eit_icecube.evaluate import load_config, run_benchmark

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_config(ROOT / 'configs/benchmark_v0.1.json')
        cls.result = run_benchmark(cls.cfg)

    def test_reference_bytes(self):
        expected = json.loads((ROOT / 'examples/reference_results.json').read_text('utf-8'))
        self.assertEqual(self.result, expected)

    def test_reject_extra_config(self):
        path = ROOT / 'configs/benchmark_v0.1.json'
        self.assertNotIn('truth', load_config(path))

    def test_all_scenarios_tested(self):
        self.assertEqual(set(self.result['scenarios']), {'clean', 'contaminated', 'dropout_contaminated'})

    def test_no_unrealistic_icecube_claim(self):
        self.assertIn('UNVALIDATED', self.result['scientific_status'])
        self.assertIn('toy', self.result['type'])

    def test_clean_negative_control(self):
        clean = self.result['scenarios']['clean']
        self.assertLess(clean['ols']['median_angular_error_deg'], 1)
        self.assertLess(clean['eit_stateful_irls']['median_angular_error_deg'], 1)

    def test_contaminated_regression_gate(self):
        c = self.result['scenarios']['contaminated']
        self.assertGreater(c['median_error_delta_ols_minus_candidate_deg'], 0)

    def test_dropout_regression_gate(self):
        c = self.result['scenarios']['dropout_contaminated']
        self.assertGreater(c['median_error_delta_ols_minus_candidate_deg'], 0)

    def test_false_positive_rate_bounded(self):
        for s in self.result['scenarios'].values():
            for m in ('ols', 'eit_stateful_irls'):
                self.assertGreaterEqual(s[m]['false_positive_rate'], 0)
                self.assertLessEqual(s[m]['false_positive_rate'], 1)

    def test_no_energy_or_real_neutrino_calibration(self):
        self.assertNotIn('energy_eV', json.dumps(self.result))
        self.assertIn('NOT neutrino energy', json.dumps(self.result))

    def test_nonempty_bootstrap(self):
        for s in self.result['scenarios'].values():
            for m in ('ols', 'eit_stateful_irls'):
                self.assertIsNotNone(s[m]['mean_bootstrap_spread_deg'])

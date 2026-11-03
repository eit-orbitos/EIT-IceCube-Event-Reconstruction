"""Regression snapshots for documented weakness and fail-closed behavior."""
import json
import unittest
from pathlib import Path
from tools.adversarial_regression import run_all
ROOT=Path(__file__).resolve().parents[1]

class AdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=run_all()
        cls.snapshot=json.loads((ROOT/'examples/adversarial_reference_v0.1.2.json').read_text())

    def test_posthoc_regression_is_byte_consistent_as_data(self):
        self.assertEqual(self.out,self.snapshot)

    def test_near_coplanar_rejected_without_direction(self):
        e=self.out['cases']['near_coplanar']
        self.assertEqual(e['median_angular_error_deg'],{'ols':None,'eit_stateful_irls':None})
        self.assertEqual(e['rejected'],{'ols':120,'eit_stateful_irls':120})

    def test_asymmetric_late_light_limitation_recorded(self):
        e=self.out['cases']['late_50pct']
        self.assertEqual(e['rejected'],{'ols':0,'eit_stateful_irls':0})
        self.assertGreater(e['median_angular_error_deg']['eit_stateful_irls'],1.0)

    def test_leverage_limitation_recorded(self):
        e=self.out['cases']['leverage_20pct']
        self.assertGreater(e['median_angular_error_deg']['eit_stateful_irls'],1.0)

    def test_correlated_shift_non_superiority(self):
        e=self.out['cases']['correlated_shift_40pct']
        self.assertGreater(e['median_angular_error_deg']['eit_stateful_irls'],
                           e['median_angular_error_deg']['ols'])

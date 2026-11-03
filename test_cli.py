import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def test_help(self):
        cmd = [sys.executable, '-m', 'eit_icecube', '--help']
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('benchmark', p.stdout)

    def test_benchmark_output(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'result.json'
            cmd = [sys.executable, '-m', 'eit_icecube', 'benchmark', '--out', str(path)]
            p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(path.read_text()), json.loads((ROOT / 'examples/reference_results.json').read_text()))

    def test_generate_separate_files(self):
        with tempfile.TemporaryDirectory() as td:
            hits, truth = Path(td) / 'hits.jsonl', Path(td) / 'truth.jsonl'
            cmd = [sys.executable, '-m', 'eit_icecube', 'generate', '--hits-out', str(hits), '--truth-out', str(truth)]
            p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(len(hits.read_text().splitlines()), 120)
            self.assertEqual(len(truth.read_text().splitlines()), 120)
            self.assertNotIn('direction_xyz', hits.read_text())
            self.assertIn('direction_xyz', truth.read_text())

    def test_prevent_truth_output_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'file.jsonl'
            cmd = [sys.executable, '-m', 'eit_icecube', 'generate', '--hits-out', str(p), '--truth-out', str(p)]
            s = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(s.returncode, 0)
            self.assertFalse(p.exists())

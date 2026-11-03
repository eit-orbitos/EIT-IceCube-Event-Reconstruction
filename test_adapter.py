import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from eit_icecube.adapter import load_single_event_csv

ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def test_csv_mapping_odf_style(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'in.csv'
            path.write_text('q,t,x,y,z\n1.2,10000,3,4,5\n', encoding='utf-8')
            event = load_single_event_csv(path)
            self.assertEqual(event['hits'][0]['x_m'], 3.0)
            self.assertEqual(event['hits'][0]['charge_au'], 1.2)

    def test_csv_mapping_canonical(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'in.csv'
            path.write_text('x_m,y_m,z_m,t_ns,charge_au\n3,4,5,6,7\n', encoding='utf-8')
            self.assertEqual(load_single_event_csv(path)['hits'][0]['t_ns'], 6)

    def test_csv_missing_columns(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'in.csv'
            path.write_text('x,y,z\n1,2,3\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_single_event_csv(path)

    def test_csv_reject_bad_numeric(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'in.csv'
            path.write_text('q,t,x,y,z\n1.2,not-a-time,3,4,5\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_single_event_csv(path)

    def test_csv_cli_no_physics_claim(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'event.csv'
            with path.open('w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['x_m', 'y_m', 'z_m', 't_ns', 'charge_au'])
                for idx in range(30):
                    x, y, z = idx*17%47, idx*11%53, idx*23%59
                    writer.writerow([x, y, z, 10000 + 4.44*(x+y+z)/3**0.5, 1.0])
            proc = subprocess.run([sys.executable, '-m', 'eit_icecube', 'reconstruct-csv', '--input', str(path)],
                                  cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            res = json.loads(proc.stdout)
            self.assertFalse(res['physical_neutrino_direction_or_energy_claim'])
            self.assertIn('UNVALIDATED', res['scientific_status'])

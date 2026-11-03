import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED
from tools.build_release import create_archive, PROJECT
from tools.verify_release import IntegrityError, verify_archive

ROOT = Path(__file__).resolve().parents[1]


class ReleaseIntegrityTests(unittest.TestCase):
    def test_build_twice_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td)/'a.zip', Path(td)/'b.zip'
            create_archive(ROOT, a)
            create_archive(ROOT, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_verify_build_from_source(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / 'a.zip'
            create_archive(ROOT, archive)
            result = verify_archive(archive, ROOT)
            self.assertEqual(result['canonical_zip'], 'PASS')
            self.assertTrue(result['regenerated_source_byte_identical'])

    def test_manifest_is_not_self_hashed(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / 'a.zip'
            create_archive(ROOT, archive)
            with ZipFile(archive) as z:
                manifest = json.loads(z.read(PROJECT+'/MANIFEST.json'))
                self.assertNotIn('MANIFEST.json', manifest['payload_files'])
                self.assertNotIn('SHA256SUMS.txt', manifest['payload_files'])
                self.assertGreater(manifest['payload_file_count'], 20)

    def test_no_dir_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / 'path.zip'
            with ZipFile(archive, 'w') as z:
                z.writestr(PROJECT + '/../intruder.txt', b'no')
            with self.assertRaises(IntegrityError):
                verify_archive(archive)

    def test_reject_checksum_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / 'a.zip'
            tampered = Path(td) / 'tampered.zip'
            create_archive(ROOT, archive)
            with ZipFile(archive) as original, ZipFile(tampered, 'w') as output:
                for info in original.infolist():
                    buf = original.read(info.filename)
                    if info.filename.endswith('/README.md'):
                        buf += b'\nTAMPER\n'
                    output.writestr(info, buf)
            with self.assertRaises(IntegrityError):
                verify_archive(tampered)

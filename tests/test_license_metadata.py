"""License-only version consistency gates (no scientific certification)."""
import json
import unittest
from pathlib import Path
from tools.build_release import PROJECT
from eit_icecube import __version__
ROOT = Path(__file__).resolve().parents[1]
LIC = "PolyForm-Noncommercial-1.0.0"
URL = "https://polyformproject.org/licenses/noncommercial/1.0.0"
class LicenseMetadataTests(unittest.TestCase):
    def test_version_and_project(self):
        self.assertEqual(__version__, "0.1.2")
        self.assertEqual(PROJECT, "EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2")
    def test_license_notice(self):
        s = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Required Notice: Copyright 2026 Toni Mladenovski", s)
        self.assertIn(URL, s)
        self.assertIn("SPDX-License-Identifier: " + LIC, s)
        self.assertNotIn("MIT License", s)
    def test_zenodo_spdx(self):
        md = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
        self.assertEqual(md["license"], LIC)
        self.assertEqual(md["version"], "0.1.2")
        self.assertTrue(md["access_right"] == "open")
        self.assertFalse(any("affiliation" in key.lower() for creator in md["creators"] for key in creator))
    def test_citation_metadata(self):
        s = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn("license: " + LIC, s)
        self.assertIn("version: 0.1.2", s)
    def test_documentation_restriction(self):
        for rel in ("README.md", "docs/RELEASE_CHECKLIST.md", "docs/DATA_PROVENANCE.md"):
            s = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("Noncommercial", s, rel)
        self.assertIn("NOT_FROZEN", (ROOT / "README.md").read_text(encoding="utf-8"))
    def test_algorithms_not_promoted(self):
        s=(ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('scientific', s.lower())
        self.assertIn('unvalidated', s.lower())

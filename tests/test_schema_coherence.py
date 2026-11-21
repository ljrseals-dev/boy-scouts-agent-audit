from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from check_schema_coherence import validate

ROOT = Path(__file__).resolve().parents[1]

class SchemaCoherenceTests(unittest.TestCase):
    def test_repository_schema_is_coherent(self):
        self.assertEqual(validate(ROOT), [])

    def test_phantom_documented_event_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "schemas").mkdir()
            schema = json.loads((ROOT / "schemas/audit_event.v2.json").read_text())
            (root / "schemas/audit_event.v2.json").write_text(json.dumps(schema))
            (root / "INVARIANTS.md").write_text("A phantom event: `phantom.injected`\n")
            errors = validate(root)
            self.assertTrue(any("phantom.injected" in error for error in errors))

    def test_nullable_or_unbounded_cap_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "schemas").mkdir()
            schema = json.loads((ROOT / "schemas/audit_event.v2.json").read_text())
            schema["properties"]["caps"]["properties"]["token_budget"] = {
                "type": ["integer", "null"]
            }
            (root / "schemas/audit_event.v2.json").write_text(json.dumps(schema))
            (root / "INVARIANTS.md").write_text("")
            errors = validate(root)
            self.assertTrue(any("caps.token_budget" in error for error in errors))

if __name__ == "__main__":
    unittest.main()

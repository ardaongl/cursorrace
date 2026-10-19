import json
import unittest
from cursorrace.report import serialize,error
from tests.support import FIXTURES
from tests.test_oracle import audit
from tests.safety import SafetyMixin


class ReportTests(SafetyMixin, unittest.TestCase):
    def test_all_analysis_goldens_and_repeatability(self):
        cases=json.loads((FIXTURES/'manifest.json').read_text())['cases']
        for case in cases:
            if case['exit_code']==2: continue
            value=json.loads((FIXTURES/case['input']).read_text())
            with self.subTest(case=case['id']):
                first=serialize(audit(value)).encode()
                self.assertEqual(first,(FIXTURES/case['stdout']).read_bytes())
                self.assertEqual(first,serialize(audit(value)).encode())

    def test_canonical_and_error_privacy(self):
        self.assertEqual(serialize({'b':'é','a':{'z':1,'x':2}}),'{'+'"a":{"x":2,"z":1},"b":"\\u00e9"}\n')
        self.assertEqual(serialize(error('JSON','')),'{"error":{"code":"JSON","pointer":""},"schema_version":1,"status":"error"}\n')

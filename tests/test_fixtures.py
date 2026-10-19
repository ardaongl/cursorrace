import unittest
from tests.fixture_gate import run_gate


class InstalledFixtureTests(unittest.TestCase):
    def test_every_installed_fixture(self):
        cases=run_gate()
        self.assertEqual(len(cases),17)
        self.assertEqual([sum(c['exit_code']==i for c in cases) for i in range(3)],[3,10,4])

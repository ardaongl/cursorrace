import copy
import json
import unittest
from cursorrace.decode import decode
from cursorrace.model import InputError
from tests.schema_assert import accepts
from tests.support import ROOT,FIXTURES,raw,trace,page


class SchemaTests(unittest.TestCase):
    def test_fixture_and_report_shapes(self):
        trace_schema=json.loads((ROOT/'schemas/trace-v1.schema.json').read_text())
        report_schema=json.loads((ROOT/'schemas/report-v1.schema.json').read_text())
        for c in json.loads((FIXTURES/'manifest.json').read_text())['cases']:
            with self.subTest(case=c['id']):
                self.assertTrue(accepts(json.loads((FIXTURES/c['stdout']).read_text()),report_schema))
                structural=c['id'] not in ('invalid-version','invalid-no-page')
                self.assertEqual(accepts(json.loads((FIXTURES/c['input']).read_text()),trace_schema),structural)

    def test_runtime_shape_agreement_for_adversarial_values(self):
        schema=json.loads((ROOT/'schemas/trace-v1.schema.json').read_text())
        for field,values in [('page_size',[0,1,1000,1001,True,'1']),('snapshot',[[],['a'],['a','a'],['a\n'],['é']]),('policy',['snapshot','live',True]),('events',[[page()],[],[{'type':'update','id':'x'}]])]:
            for value in values:
                t=trace();t[field]=value
                with self.subTest(field=field,value=value):
                    try:decode(raw(t));actual=True
                    except InputError:actual=False
                    self.assertEqual(actual,accepts(t,schema))

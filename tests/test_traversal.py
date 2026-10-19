import unittest
from tests.test_oracle import audit,findings
from tests.support import page,trace


class TraversalTests(unittest.TestCase):
    def test_incomplete_never_reports_missing(self):
        self.assertEqual(findings(trace(['a','b'],[page(['a'],next='k')])),[('INCOMPLETE','/events/0/next_cursor',None)])
        self.assertEqual(findings(trace(['a','b'],[page(['a']),page([],None,'k')])),[
            ('AFTER_TERMINAL','/events/1',None),('INCOMPLETE','/events/1/next_cursor',None)])

    def test_first_request_chain_and_cycle_across_mutations(self):
        t=trace(['a','b'],[page(['a'],next='k'),{'type':'insert','id':'x'},page(['b'],'k','m'),page([],'m','k')])
        self.assertEqual(findings(t),[('CURSOR_CYCLE','/events/3/next_cursor',None),('INCOMPLETE','/events/3/next_cursor',None)])
        self.assertEqual(findings(trace([], [page([],request='wrong')])),[('CHAIN_MISMATCH','/events/0/request_cursor',None)])

    def test_terminal_persists_and_checks_continue(self):
        t=trace(['a','b'],[page(['a']),{'type':'insert','id':'x'},page(['b'],'wrong')])
        self.assertEqual(findings(t),[('AFTER_TERMINAL','/events/1',None),('AFTER_TERMINAL','/events/2',None),('CHAIN_MISMATCH','/events/2/request_cursor',None)])

    def test_opaque_tokens_are_not_interpreted(self):
        token='https://example.invalid/a?secret=!%2F'
        self.assertEqual(audit(trace(['a'],[page([],next=token),page(['a'],token)]))['status'],'pass')

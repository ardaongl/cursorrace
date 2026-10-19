import itertools
import unittest

from cursorrace.check import check
from cursorrace.decode import decode
from cursorrace.ledger import validate
from tests.support import page, trace, raw


def audit(value):
    t=decode(raw(value));validate(t);return check(t)


def findings(value):
    return [(f['code'],f['pointer'],f['id']) for f in audit(value)['findings']]


class SnapshotTests(unittest.TestCase):
    def test_frozen_membership_despite_mutations(self):
        events=[page(['a'],next='k'),{'type':'delete','id':'b'},{'type':'insert','id':'x'},page(['b','c'],'k')]
        self.assertEqual(audit(trace(['a','b','c'],events))['status'],'pass')
        events[-1]=page(['c'],'k')
        self.assertEqual(findings(trace(['a','b','c'],events)),[('MISSING_ID','/snapshot/1','b')])
        events[-1]=page(['b','x','c'],'k')
        self.assertEqual(findings(trace(['a','b','c'],events,size=3)),[('UNEXPECTED_ID','/events/3/ids/1','x')])

    def test_empty_and_short_pages_and_partition_invariance(self):
        self.assertEqual(audit(trace())['status'],'pass')
        # Every split into three pages, including empty leading/interior/tail pages.
        snapshot=['z','a','m']  # Caller order is authoritative, not lexical order.
        for a,b in itertools.combinations_with_replacement(range(4),2):
            with self.subTest(a=a,b=b):
                result=audit(trace(snapshot,[page(snapshot[:a],next='x'),page(snapshot[a:b],'x','y'),page(snapshot[b:],'y')],size=3))
                self.assertEqual(result['status'],'pass')
                self.assertEqual(result['stats'],dict(snapshot_count=3,page_count=3,mutation_count=0,observed_count=3))

    def test_missing_in_snapshot_order(self):
        self.assertEqual(findings(trace(['z','a','m'],[page(['a'])])),[('MISSING_ID','/snapshot/0','z'),('MISSING_ID','/snapshot/2','m')])


class FindingTests(unittest.TestCase):
    def test_duplicates_and_unknowns_accumulate(self):
        self.assertEqual(findings(trace(['a'],[page(['a','x','x'])],size=3)),[
            ('UNEXPECTED_ID','/events/0/ids/1','x'),('DUPLICATE_ID','/events/0/ids/2','x'),('UNEXPECTED_ID','/events/0/ids/2','x')])

    def test_cross_page_order_ignores_unknowns_and_tracks_duplicates(self):
        self.assertEqual(findings(trace(['a','b','c'],[page(['c'],next='k'),page(['x','a','a','b'],'k')],size=4)),[
            ('UNEXPECTED_ID','/events/1/ids/0','x'),('OUT_OF_ORDER','/events/1/ids/1','a'),('DUPLICATE_ID','/events/1/ids/2','a')])
        self.assertEqual(findings(trace(['a','b'],[page(['a','b','a'])],size=3)),[
            ('DUPLICATE_ID','/events/0/ids/2','a'),('OUT_OF_ORDER','/events/0/ids/2','a')])

    def test_page_checks_precede_items(self):
        self.assertEqual(findings(trace(['a'],[page(['x','a'],request='k',next='k')],size=1)),[
            ('CHAIN_MISMATCH','/events/0/request_cursor',None),('CURSOR_CYCLE','/events/0/next_cursor',None),
            ('PAGE_OVERFLOW','/events/0/ids',None),('UNEXPECTED_ID','/events/0/ids/0','x'),('INCOMPLETE','/events/0/next_cursor',None)])

import copy
import unittest

from cursorrace.decode import MAX_BYTES, decode
from cursorrace.ledger import validate
from cursorrace.model import InputError
from tests.support import raw, page, trace


class ValidationTests(unittest.TestCase):
    def reject(self, data, code, pointer=None):
        with self.assertRaises(InputError) as caught:
            validate(decode(data))
        self.assertEqual(caught.exception.code, code)
        if pointer is not None:
            self.assertEqual(caught.exception.pointer, pointer)

    def test_byte_limits_and_precedence(self):
        data = raw(trace())
        decode(data + b' ' * (MAX_BYTES-len(data)))
        self.reject(data + b' ' * (MAX_BYTES+1-len(data)), 'LIMIT', '')
        self.reject(b'\xff' * (MAX_BYTES+1), 'LIMIT', '')

    def test_encoding_and_invalid_json(self):
        for data, code in [(b'', 'JSON'), (b'\xef\xbb\xbf{}', 'ENCODING'), (b'\xff', 'ENCODING'),
                           (b'{}{}', 'JSON'), (b'{', 'JSON'), (b'{"x":1,"x":2}', 'JSON'),
                           (b'{"x":1,"\\u0078":2}', 'JSON'), (b'"\\ud800"','JSON')]:
            with self.subTest(data=data): self.reject(data,code,'')
        for number in [b'1.0',b'1e0',b'NaN',b'Infinity',b'-Infinity']:
            self.reject(raw(trace()).replace(b'"page_size":2', b'"page_size":'+number), 'JSON', '')

    def test_oversized_integer_lexemes(self):
        for n in [5000, MAX_BYTES-200]:
            data=raw(trace()).replace(b'"page_size":2',b'"page_size":'+b'9'*n)
            self.assertLessEqual(len(data), MAX_BYTES)
            self.reject(data,'SCHEMA','/page_size')
        self.reject(b'{"x":01}', 'JSON','')

    def test_depth_and_quoted_delimiters(self):
        self.reject(b'['*16+b'0'+b']'*16, 'SCHEMA','')
        self.reject(b'['*17+b'0'+b']'*17, 'LIMIT','')
        t=trace(events=[page(next='['*100 + '\\"' + ']'*100)])
        decode(raw(t))

    def test_root_keys_and_types(self):
        for v in [None,[],True,1,'a']:
            self.reject(raw(v),'SCHEMA','')
        for key in trace():
            t=trace(); del t[key]; self.reject(raw(t),'SCHEMA','/'+key)
        for path in [('extra',), ('events',0,'extra')]:
            t=trace(); target=t
            for k in path[:-1]: target=target[k]
            target[path[-1]]=0; self.reject(raw(t),'SCHEMA')
        for v in [True,False,0,2,'1',None,{},[]]:
            t=trace(); t['schema_version']=v; self.reject(raw(t),'SCHEMA','/schema_version')
        t=trace();t['policy']='live';self.reject(raw(t),'SCHEMA','/policy')

    def test_string_boundaries(self):
        for value in ['a','a'*64,'A_:.0-']:
            decode(raw(trace([value])))
        for value in ['', 'a'*65, '-a','a\n','a b','é',True,None,0]:
            self.reject(raw(trace([value])),'SCHEMA','/snapshot/0')
        for value in [None,'x','x'*256,'https://example.invalid/[!]']:
            decode(raw(trace(events=[page(next=value)])))
        for value in ['', 'x'*257, 'a b','x\n','é',False,[],{}]:
            self.reject(raw(trace(events=[page(next=value)])),'SCHEMA','/events/0/next_cursor')
        decode(b'{"schema_version":1,"policy":"snapshot","snapshot":["\\u0061"],"page_size":1,"events":[{"type":"page","request_cursor":null,"ids":["a"],"next_cursor":null}]}')

    def test_cardinalities(self):
        for n in [1,1000]: decode(raw(trace(size=n)))
        for n in [0,1001,True,None,'2']:
            self.reject(raw(trace(size=n)),'SCHEMA','/page_size')
        for n in [0,10000]: decode(raw(trace([f'a{i}' for i in range(n)])))
        self.reject(raw(trace([f'a{i}' for i in range(10001)])),'SCHEMA','/snapshot')
        self.reject(raw(trace(['a','a'])),'SCHEMA','/snapshot/1')
        for n in [0,1000]: decode(raw(trace(events=[page(['a']*n)])))
        self.reject(raw(trace(events=[page(['a']*1001)])),'SCHEMA','/events/0/ids')
        # Compact write events keep the 10,000-event boundary under the byte cap.
        for n in [1,10000]: decode(raw(trace(events=[page()]+[{'type':'insert','id':'a'}]*(n-1))))
        for n in [0,10001]: self.reject(raw(trace(events=[page()]+[{'type':'insert','id':'a'}]*(n-1) if n else [])),'SCHEMA','/events')
        decode(raw(trace(events=[page(['a']*1000)]*100)))
        self.reject(raw(trace(events=[page(['a']*1000)]*100+[page(['a'])])),'LIMIT','/events')

    def test_event_shapes_and_ledger(self):
        for event in [None,[],{}, {'type':'update','id':'a'}, {'type':'page'}, {'type':'insert','id':'a','extra':1}]:
            self.reject(raw(trace(events=[event])),'SCHEMA')
        self.reject(raw(trace(events=[{'type':'insert','id':'x'}])),'SCHEMA','/events')
        for snapshot, mutations in [(['a'],[('insert','a')]),([], [('delete','x')]),(['a'],[('delete','a'),('delete','a')]),(['a'],[('delete','a'),('insert','a')]),([], [('insert','a'),('insert','a')])]:
            self.reject(raw(trace(snapshot,[page()]+[{'type':k,'id':v} for k,v in mutations])),'LEDGER')
        validate(decode(raw(trace(['a'],[{'type':'insert','id':'b'},{'type':'delete','id':'b'},page(['a'])]))))

    def test_whole_tail_validated_before_analysis(self):
        self.reject(raw(trace(['a'],[page(['a','a']),{'type':'delete','id':'z'}])),'LEDGER','/events/1/id')

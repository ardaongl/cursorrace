"""Independent evaluator for the keywords used by the two published schemas.

Test tooling only: not a general JSON Schema implementation or product validator.
Lexical/ledger/resource rules outside the declarative schema are tested separately.
"""
import json
import re


def accepts(value,schema,root=None):
    root = schema if root is None else root
    if '$ref' in schema:
        target=root
        for part in schema['$ref'].split('/')[1:]:target=target[part]
        return accepts(value,target,root)
    if 'oneOf' in schema and sum(accepts(value,s,root) for s in schema['oneOf'])!=1:return False
    if 'not' in schema and accepts(value,schema['not'],root):return False
    types=schema.get('type',[]);types=[types] if isinstance(types,str) else types
    kind={'null':value is None,'string':isinstance(value,str),'integer':type(value) is int or (type(value) is float and value.is_integer()),'object':type(value) is dict,'array':type(value) is list}
    if types and not any(kind.get(t,False) for t in types):return False
    def same(a,b):return type(a) is type(b) and a==b or type(a) in (int,float) and type(b) in (int,float) and a==b
    if 'const' in schema and not same(value,schema['const']):return False
    if 'enum' in schema and not any(same(value,x) for x in schema['enum']):return False
    if type(value) is dict:
        if not all(k in value for k in schema.get('required',[])):return False
        props=schema.get('properties',{})
        if schema.get('additionalProperties') is False and set(value)-set(props):return False
        if not all(accepts(v,props[k],root) for k,v in value.items() if k in props):return False
    if type(value) is list:
        if not schema.get('minItems',0)<=len(value)<=schema.get('maxItems',float('inf')):return False
        if 'items' in schema and not all(accepts(v,schema['items'],root) for v in value):return False
        if schema.get('uniqueItems') and len({json.dumps(v,sort_keys=True) for v in value})!=len(value):return False
        if 'contains' in schema and not any(accepts(v,schema['contains'],root) for v in value):return False
    if isinstance(value,str):
        if len(value)>schema.get('maxLength',float('inf')):return False
        if 'pattern' in schema and re.search(schema['pattern'],value) is None:return False
    if type(value) in (int,float):
        if not schema.get('minimum',-float('inf'))<=value<=schema.get('maximum',float('inf')):return False
    return True

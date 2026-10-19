"""Strict bounded UTF-8/JSON and shape validation, using only the stdlib."""
import json
import re

from .model import InputError, Mutation, Page, Trace

MAX_BYTES = 1_048_576
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}", re.ASCII)
_CURSOR = re.compile(r"[!-~]{1,256}", re.ASCII)
_LARGE_INTEGER = object()


def _depth(text: str) -> None:
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > 16:
                raise InputError("LIMIT")
        elif char in "]}":
            depth -= 1


def _integer(lexeme: str):
    # Every allowed integer field is <=1000. Preserve shape rejection without
    # converting attacker-controlled huge integers or changing interpreter limits.
    if len(lexeme.lstrip("-")) > 5:
        return _LARGE_INTEGER
    return int(lexeme)


def _reject_number(_):
    raise InputError("JSON")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("JSON")
        result[key] = value
    return result


def _unicode(value) -> None:
    if isinstance(value, str):
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            raise InputError("JSON")
    elif isinstance(value, dict):
        for key, item in value.items():
            _unicode(key)
            _unicode(item)
    elif isinstance(value, list):
        for item in value:
            _unicode(item)


def _pointer(parent, key):
    return parent + "/" + str(key).replace("~", "~0").replace("/", "~1")


def _object(value, keys, pointer):
    if type(value) is not dict:
        raise InputError("SCHEMA", pointer)
    mismatch = set(value) ^ set(keys)
    if mismatch:
        raise InputError("SCHEMA", _pointer(pointer, sorted(mismatch)[0]))


def _array(value, maximum, pointer, minimum=0):
    if type(value) is not list or not minimum <= len(value) <= maximum:
        raise InputError("SCHEMA", pointer)


def _id(value, pointer):
    if type(value) is not str or not _ID.fullmatch(value):
        raise InputError("SCHEMA", pointer)


def _cursor(value, pointer):
    if value is not None and (type(value) is not str or not _CURSOR.fullmatch(value)):
        raise InputError("SCHEMA", pointer)


def decode(data: bytes) -> Trace:
    if len(data) > MAX_BYTES:
        raise InputError("LIMIT")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError("ENCODING") from None
    if text.startswith("\ufeff"):
        raise InputError("ENCODING")
    _depth(text)
    try:
        value = json.loads(text, object_pairs_hook=_pairs, parse_int=_integer,
                           parse_float=_reject_number, parse_constant=_reject_number)
    except (ValueError, RecursionError):
        raise InputError("JSON") from None
    _unicode(value)
    _object(value, ("schema_version", "policy", "snapshot", "page_size", "events"), "")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise InputError("SCHEMA", "/schema_version")
    if value["policy"] != "snapshot":
        raise InputError("SCHEMA", "/policy")
    size = value["page_size"]
    if type(size) is not int or not 1 <= size <= 1000:
        raise InputError("SCHEMA", "/page_size")
    snapshot = value["snapshot"]
    _array(snapshot, 10000, "/snapshot")
    seen = set()
    for i, item in enumerate(snapshot):
        pointer = f"/snapshot/{i}"
        _id(item, pointer)
        if item in seen:
            raise InputError("SCHEMA", pointer)
        seen.add(item)
    _array(value["events"], 10000, "/events", 1)
    events = []
    count = pages = 0
    for i, event in enumerate(value["events"]):
        pointer = f"/events/{i}"
        if type(event) is not dict:
            raise InputError("SCHEMA", pointer)
        kind = event.get("type")
        if kind == "page":
            _object(event, ("type", "request_cursor", "ids", "next_cursor"), pointer)
            _cursor(event["request_cursor"], pointer + "/request_cursor")
            _cursor(event["next_cursor"], pointer + "/next_cursor")
            _array(event["ids"], 1000, pointer + "/ids")
            for j, item in enumerate(event["ids"]):
                _id(item, pointer + f"/ids/{j}")
            events.append(Page(event["request_cursor"], tuple(event["ids"]), event["next_cursor"]))
            count += len(event["ids"])
            pages += 1
        elif kind in ("insert", "delete"):
            _object(event, ("type", "id"), pointer)
            _id(event["id"], pointer + "/id")
            events.append(Mutation(kind, event["id"]))
        else:
            raise InputError("SCHEMA", pointer + "/type")
    if not pages:
        raise InputError("SCHEMA", "/events")
    if count > 100000:
        raise InputError("LIMIT", "/events")
    return Trace(tuple(snapshot), size, tuple(events))

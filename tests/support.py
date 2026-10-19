from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def page(ids=(), request=None, next=None):
    return {"type": "page", "request_cursor": request, "ids": list(ids), "next_cursor": next}


def trace(snapshot=(), events=None, size=2):
    return {"schema_version": 1, "policy": "snapshot", "snapshot": list(snapshot),
            "page_size": size, "events": [page()] if events is None else events}


def raw(value):
    return json.dumps(value, separators=(",", ":")).encode()

"""Canonical machine output. Never include raw parser exceptions or cursors."""
import json


def serialize(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def error(code, pointer):
    return {"schema_version": 1, "status": "error", "error": {"code": code, "pointer": pointer}}

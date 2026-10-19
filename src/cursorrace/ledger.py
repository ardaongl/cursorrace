"""Validate the caller's write ledger without changing the frozen oracle."""
from .model import InputError, Mutation, Trace


def validate(trace: Trace) -> None:
    live = set(trace.snapshot)
    ever = set(live)
    for i, event in enumerate(trace.events):
        if not isinstance(event, Mutation):
            continue
        if event.type == "insert":
            if event.id in ever:
                raise InputError("LEDGER", f"/events/{i}/id")
            live.add(event.id)
            ever.add(event.id)
        else:
            if event.id not in live:
                raise InputError("LEDGER", f"/events/{i}/id")
            live.remove(event.id)

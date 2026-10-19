"""Pure, transport-independent ordered snapshot traversal checker."""
from dataclasses import asdict

from .model import Finding, Mutation, Page, Trace


def check(trace: Trace) -> dict:
    ranks = {item: i for i, item in enumerate(trace.snapshot)}
    seen = set()
    requests = set()
    findings = []
    previous_rank = None
    previous_cursor = None
    terminal_seen = False
    page_count = observed_count = mutation_count = 0
    last_page = None
    last_index = None

    def emit(code, pointer, id=None):
        findings.append(Finding(code, pointer, id))

    for i, event in enumerate(trace.events):
        pointer = f"/events/{i}"
        if terminal_seen:
            emit("AFTER_TERMINAL", pointer)
        if isinstance(event, Mutation):
            mutation_count += 1
            continue
        page_count += 1
        observed_count += len(event.ids)
        if event.request_cursor != previous_cursor:
            emit("CHAIN_MISMATCH", pointer + "/request_cursor")
        if event.request_cursor is not None:
            requests.add(event.request_cursor)
        if event.next_cursor is not None and event.next_cursor in requests:
            emit("CURSOR_CYCLE", pointer + "/next_cursor")
        if len(event.ids) > trace.page_size:
            emit("PAGE_OVERFLOW", pointer + "/ids")
        for j, item in enumerate(event.ids):
            item_pointer = pointer + f"/ids/{j}"
            if item in seen:
                emit("DUPLICATE_ID", item_pointer, item)
            if item not in ranks:
                emit("UNEXPECTED_ID", item_pointer, item)
            else:
                rank = ranks[item]
                if previous_rank is not None and rank < previous_rank:
                    emit("OUT_OF_ORDER", item_pointer, item)
                previous_rank = rank
            seen.add(item)
        previous_cursor = event.next_cursor
        terminal_seen |= event.next_cursor is None
        last_page, last_index = event, i
    if last_page.next_cursor is not None:
        emit("INCOMPLETE", f"/events/{last_index}/next_cursor")
    else:
        for j, item in enumerate(trace.snapshot):
            if item not in seen:
                emit("MISSING_ID", f"/snapshot/{j}", item)
    return {
        "schema_version": 1,
        "status": "fail" if findings else "pass",
        "stats": {"snapshot_count": len(trace.snapshot), "page_count": page_count,
                  "mutation_count": mutation_count, "observed_count": observed_count},
        "findings": [asdict(finding) for finding in findings],
    }

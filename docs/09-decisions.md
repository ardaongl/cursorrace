# Architecture decisions

These decisions define the proposed v1 implementation under the selected spec scope; they do not authorize a build or remote operation.

## ADR-001 — Offline normalized trace rather than live runner

Status: SELECTED_FOR_SPEC (2026-10-19). Live scheduling would require auth, reset, transport and cleanup contracts. Select file-in/JSON-out verification with caller-owned capture. Keeps dependency/network scope small and failures reproducible. Consequence: cannot reproduce races or prove the trace was honestly captured. Verify byte goldens, no execution-time network and the application-level no-write boundary with its CPython-managed bytecode exception (AC-05/07).

## ADR-002 — Snapshot-at-start policy only

Status: SELECTED_FOR_SPEC. Live keyset pagination and snapshot export have different legitimate missing/new-row behaviors. Select immutable ordered ID sequence, regardless of later writes. User supplies total order including any tie-break. No payload checking, row updates or identity reuse. Deleted original b remains expected, inserted x unexpected. Reject unsupported policies rather than guessing. Verify deleted-gap and inserted-ID fixtures (AC-01/04).

## ADR-003 — Whole-file validation before ordered analysis

Status: SELECTED_FOR_SPEC. Streaming could lower memory but invites partial results on malformed ledger tails. One MiB cap makes full validation practical. Reject malformed/ambiguous input with exit2, then accumulate deterministic domain findings with exit1. Missing only on a terminal final page prevents claiming absence from truncated traces. Verify tail-invalid precedence, size boundaries and incomplete goldens (AC-03/04).

## ADR-004 — Observed modern Python and stdlib runtime

Status: SELECTED_FOR_SPEC. Codex execution exposed system Python3.9.6 and a usable Python3.14.8/pip26.2.1 at Homebrew path. Select CPython3.14.8, stdlib CLI/JSON/unittest, setuptools80.9.0 isolated backend; no runtime dependencies. This is a pinned baseline, not a claim about the globally newest runtime. Reverify in preflight and use portable discovery, never product-hardcode host paths. Exact artifact bootstrap and CI install remain later executed evidence (AC-08).

## ADR-005 — Opaque token privacy and stable machine report

Status: SELECTED_FOR_SPEC. Tokens can carry sensitive data, while IDs are necessary for useful membership diagnostics. Exclude token values and raw parser exceptions; include synthetic/user IDs with stable code/pointer locations. JSON-only sorted compact output avoids reporter variants. Users must scrub IDs before sharing. Verify canary tokens, canonical bytes and stream failures (AC-05/06).

# Architecture

## Boundaries

Developer-owned integration harness → normalized UTF-8 trace file → CursorRace CLI → bounded reader → strict decoder/shape validator → ledger validator → pure traversal checker → report serializer → stdout.

Future package layout: `src/cursorrace/{__init__,__main__,cli,decode,model,ledger,check,report}.py`. `__main__` and console script both delegate to cli.main. Only CLI owns file/stream/process behavior. Decode validates before constructing immutable domain values; ledger validates inserts/deletes without reading cursor meaning. Checker depends only on validated values and emits ordered Finding values. Report owns canonical JSON bytes. No public Python library API in v1; internal modules may change.

Schemas in `schemas/` document portable interchange shape. Product validation uses stdlib and cross-field rules in docs/03-contracts.md; it does not fetch/load external schemas. Tests must compare runtime validation with schema cases so declarative and executable rules do not drift.

## Algorithm and state

Read at most 1 MiB +1 before decoding; no partial processing. Validate complete structure and replay complete mutation ledger first. Build snapshot rank map and live-ID set; retain a never-used-again identity set. Freeze rank map forever. Walk page events in original order, retaining previous next cursor, requested cursor set, observed ID set, prior known rank and terminal-seen flag. Emit per-event findings in contractual order. If the final page is terminal, append absent snapshot IDs in snapshot order. Serialize once.

No wall clock, random seed, application-controlled filesystem mutation, network, worker tasks or persistent storage. CPython interpreter-managed bytecode artifacts are the sole filesystem exception, as defined in [the execution boundary](03-contracts.md#privacy-compatibility-and-trust); they do not permit application logs, temporary files or caches. Mutation events reflect between-read scheduling, not temporal overlap. Full validation before checking means an invalid ledger yields only an input error, even if earlier pages visibly fail. O(input bytes + events + total returned IDs + snapshot IDs), bounded by the byte limit; memory O(input bytes). No pairwise row scans. Limit validation precedes expensive domain processing.

## Runtime and delivery

CPython 3.14.8 and pip 26.2.1 were actually observed at the local Homebrew path; system Python is 3.9.6. Preflight must reverify them in Codex's execution context. Baseline supported OSes: macOS and Ubuntu 24.04. No compatibility claim for other Python minors or Windows. Future wheel/sdist: `cursorrace`, version 0.1.0, `requires-python = ">=3.14.8,<3.15"`, entry point `cursorrace = cursorrace.cli:main`, build backend setuptools.build_meta with setuptools==80.9.0. No runtime dependency resolution required. Package includes license, README and schemas; sdist additionally includes fixtures/tests/docs. JSON file package data must not depend on CWD.

Build time network for pinned tooling is distinct from offline execution. CI action references must be immutable commit SHAs selected and verified at M4; do not invent hashes in spec. The prepared workflow is .github/workflows/ci.yml. Use stdlib unittest and subprocess; packaging gate acquires a pinned backend wheel before an offline install.

## Alternatives considered

1. Live HTTP race runner: valuable automation, but auth/reset hooks, timeout policy and database lifecycle overwhelm a micro MVP. Rejected for v1.
2. General API property/fuzz test framework: overlaps mature substitutes; far larger schema/strategy surface. Rejected.
3. Offline trace auditor (selected): deterministic, transport-neutral and cheap to distribute. Cannot prove real concurrent correctness, authenticity or snapshot acquisition independence. Exposes concrete parser, state-machine, oracle and distribution engineering depth.

Failure policy: expected bad traces are ordinary exit-1 domain reports; invalid data exits 2 before analysis; IO and unexpected runtime errors are exit 3. Stream failures can prevent a complete report and must never produce success.
